from taifun.taifun import Taifun, FunctionParameters, Function, Parameter


def test_simple():
    taifun = Taifun()

    @taifun.fn()
    def hello():
        """Say hello"""
        return "Hello"

    assert taifun.functions["hello"][0] == Function(
        name="hello",
        description="Say hello",
        parameters=FunctionParameters(properties={}, required=[]),
    )


def test_function_with_parameters():
    taifun = Taifun()

    @taifun.fn()
    def hello(name: str):
        """
        Say hello

        Parameters
        ----------
        name : str
            The name of the person to say hello to

        """
        return f"Hello {name}"

    assert taifun.functions["hello"][0] == Function(
        name="hello",
        description="Say hello",
        parameters=FunctionParameters(
            properties={
                "name": Parameter(
                    type="str",
                    description="The name of the person to say hello to",
                )
            },
            required=["name"],
        ),
    )


def test_functions_dict():
    taifun = Taifun()

    @taifun.fn()
    def hello():
        """Say hello"""
        return "Hello"

    fn_dict = taifun.functions_as_dict()
    assert fn_dict == [
        {
            "name": "hello",
            "description": "Say hello",
            "parameters": {
                "properties": {},
                "required": [],
                "type": "object",
            },
        }
    ]


def test_functions_dict_with_param():
    taifun = Taifun()

    @taifun.fn()
    def hello(name: str):
        """
        Say hello

        Parameters
        ----------
        name : str
            The name of the person to say hello to

        """
        return f"Hello {name}"

    fn_dict = taifun.functions_as_dict()
    assert fn_dict == [
        {
            "name": "hello",
            "description": "Say hello",
            "parameters": {
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the person to say hello to",
                    }
                },
                "required": ["name"],
                "type": "object",
            },
        }
    ]
