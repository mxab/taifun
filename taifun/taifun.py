import inspect
from typing import Any, Callable, Dict, Tuple, TypedDict
from docstring_parser import parse
from pydantic import Field, RootModel, create_model, BaseModel
from taifun.openai_api import Function


class FunctionCallDict(TypedDict):
    name: str
    arguments: str


class Taifun:
    def __init__(self):
        self.functions: Dict[str, Tuple[Function, Callable, BaseModel]] = {}

    def fn(self: "Taifun") -> Any:
        def inner(func):
            sig: inspect.Signature = inspect.signature(func)

            doc = inspect.getdoc(func) or ""

            parsed_docstring = parse(doc)
            # index docstring params by name
            docstring_params = {
                doc_param.arg_name: doc_param.description
                for doc_param in parsed_docstring.params
            }

            param_type_default_tuples_by_name = {}

            for param in sig.parameters.values():
                if param.name == "self":
                    continue
                if param.name == "return":
                    continue
                if param.name == "return_type":
                    continue

                description = docstring_params.get(param.name, "") or ""

                param_type_default_tuples_by_name[param.name] = (
                    param.annotation,
                    Field(
                        title=None,
                        description=description,
                        default=param.default
                        if param.default is not inspect.Parameter.empty
                        else ...,
                    ),
                )

            parameters_model: BaseModel = create_model(
                "FunctionParameters", **param_type_default_tuples_by_name
            )
            parameters_schema: dict = parameters_model.model_json_schema()

            description = "\n".join(
                filter(
                    None,
                    [
                        parsed_docstring.short_description,
                        parsed_docstring.long_description,
                    ],
                )
            ).strip()

            fn: Function = Function(
                name=func.__name__,
                description=description,
                parameters=parameters_schema,
            )
            self.functions[func.__name__] = (fn, func, parameters_model)

            def wrapper(*args, **kwargs):
                r = func(*args, **kwargs)

                return r

            return wrapper

        return inner

    def functions_as_dict(self):
        return RootModel[list[Function]](
            [fn for _, (fn, _, _) in self.functions.items()]
        ).model_dump(exclude_none=True)

    def handle_function_call(self, function_call_dict: FunctionCallDict):
        _, func, func_params_model = self.functions[function_call_dict["name"]]

        func_params = func_params_model.model_validate_json(
            function_call_dict["arguments"]
        )

        return func(**func_params.__dict__)
