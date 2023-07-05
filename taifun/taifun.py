import inspect
import json
from typing import Any, Callable, Dict, Tuple

import openai
from docstring_parser import parse

from pydantic import RootModel, Field
from taifun.openai_api import Function, Message, Role, FunctionCall
from rich.console import Console

from pydantic import create_model


class Taifun:
    def __init__(self, openai_model: str = "gpt-3.5-turbo-0613"):
        self.__end_of_conversation = False
        self.__end_conversation_reason: str | None = None
        self.functions: Dict[str, Tuple[Function, Callable]] = {}
        self.openai_model = openai_model
        self.fn()(self.__end_conversation)

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

            parameters_schema: dict = create_model(
                "FunctionParameters", **param_type_default_tuples_by_name
            ).model_json_schema()

            fn: Function = Function(
                name=func.__name__,
                description=parsed_docstring.short_description or "",
                parameters=parameters_schema,
            )
            self.functions[func.__name__] = (fn, func)

            def wrapper(*args, **kwargs):
                r = func(*args, **kwargs)

                return r

            return wrapper

        return inner

    def __end_conversation(self, reason: str = None):
        """
        Mark the end of the conversation

        Parameters
        ----------
        reason : str, optional (default=None) The reason for ending the conversation
        """
        self.__end_of_conversation = True
        self.__end_conversation_reason = reason

    def functions_as_dict(self):
        return RootModel[list[Function]](
            [fn for _, (fn, _) in self.functions.items()]
        ).model_dump(exclude_none=True)

    def call_function(self, name: str, arguments: str):
        fn, func = self.functions[name]
        return func(**json.loads(arguments))

    def run(self, task: str):
        console = Console()
        messages = [
            {
                "role": "system",
                "content": """
            You are a task assistant.
            When you are done, call the __end_of_conversation function with an optional message that tells the user why you are ending the conversation.
            """.strip(),
            },
            {"role": "user", "content": task},
        ]

        functions = self.functions_as_dict()

        while not self.__end_of_conversation:
            response = openai.ChatCompletion.create(
                model=self.openai_model,
                messages=messages,
                functions=functions,
                function_call="auto",  # auto is default, but we'll be explicit
            )
            message_dict = response["choices"][0]["message"]
            response_message = Message(
                role=message_dict["role"],
                content=message_dict["content"] or "",
                function_call=FunctionCall(name=message_dict["function_call"]["name"], arguments=message_dict["function_call"]["arguments"])
                if message_dict.get("function_call")
                else None,
            )

            messages.append(
                response_message.model_dump(exclude_none=True)
            )  # extend conversation with assistant's reply
            # Step 2: check if GPT wanted to call a function
            if response_message.function_call:
                console.print("Function call:", style="bold")
                console.print(response_message.function_call.name)

                function_name = response_message.function_call.name
                function_arguments = response_message.function_call.arguments
                function_response = self.call_function(
                    function_name, function_arguments
                )

                messages.append(
                    Message(
                        role=Role.function,
                        name=function_name,
                        content=json.dumps(function_response),
                    ).model_dump(
                        exclude_none=True
                    )
                )

            elif response_message.content:
                console.print(response_message.role, style="bold")
                console.print(response_message.content)

            else:
                raise Exception("Unknown response: " + response_message.content)

        return self.__end_conversation_reason
