from taifun.taifun import Taifun


def test_functions_dict():
    taifun = Taifun()

    @taifun.fn()
    def simple_function():
        """A simple function"""
        return "Hello"

    fn_dict = taifun.functions_as_dict()
    assert len(fn_dict) == 2

    assert fn_dict[1] == {
        "name": "simple_function",
        "description": "A simple function",
        "parameters": {
            "properties": {},
            "type": "object",
            "title": "FunctionParameters",
            "type": "object",
        },
    }


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
    assert len(fn_dict) == 2
    assert fn_dict[1] == {
        "name": "hello",
        "description": "Say hello",
        "parameters": {
            "properties": {
                "name": {
                    "type": "string",
                    "title": "Name",
                    "description": "The name of the person to say hello to",
                }
            },
            "required": ["name"],
            "title": "FunctionParameters",
            "type": "object",
        },
    }
