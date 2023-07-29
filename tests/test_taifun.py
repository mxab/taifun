from taifun.taifun import Taifun, MissingDescriptionError
from pydantic import BaseModel, Field
import json
import pytest


def test_functions_dict():
    taifun = Taifun()

    @taifun.fn()
    def simple_function():
        """A simple function"""
        return "Hello"

    fn_dict = taifun.functions_as_dict()
    assert len(fn_dict) == 1

    assert fn_dict[0] == {
        "name": "simple_function",
        "description": "A simple function",
        "parameters": {
            "properties": {},
            "type": "object",
            "title": "FunctionParameters",
            "type": "object",
        },
    }


def test_functions_dict_call():
    taifun = Taifun()

    @taifun.fn()
    def simple_function():
        """A simple function"""
        return "Hello"

    assert (
        taifun.handle_function_call(
            {
                "name": "simple_function",
                "arguments": json.dumps({}),
            }
        )
        == "Hello"
    )


def test_functions_dict_with_long_description():
    taifun = Taifun()

    @taifun.fn()
    def simple_function():
        """
        A simple function

        It does simple things. But it also has a complex description
        """
        return "Hello"

    fn_dict = taifun.functions_as_dict()
    assert len(fn_dict) == 1

    assert fn_dict[0] == {
        "name": "simple_function",
        "description": "A simple function\nIt does simple things. But it also has a complex description",
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
    assert len(fn_dict) == 1
    assert fn_dict[0] == {
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


def test_functions_dict_with_param_function_call():
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

    assert (
        taifun.handle_function_call(
            {
                "name": "hello",
                "arguments": json.dumps({"name": "World"}),
            }
        )
        == "Hello World"
    )


def test_functions_dict_with_pydantic_param():
    class Greeting(BaseModel):
        name: str = Field(
            ..., description="The name of the person that should be greeted"
        )
        salutation: str = Field(..., description="The salutation to use")

    taifun = Taifun()

    @taifun.fn()
    def hello(greeting: Greeting):
        """
        Say hello

        Parameters
        ----------
        greeting : Greeting
            The greeting to say, and the name to say it to

        """
        return f"{greeting.greeting} {greeting.name}"

    fn_dict = taifun.functions_as_dict()
    assert len(fn_dict) == 1

    assert fn_dict[0] == {
        "name": "hello",
        "description": "Say hello",
        "parameters": {
            "$defs": {
                "Greeting": {
                    "properties": {
                        "name": {
                            "description": "The name of the person that should be greeted",
                            "title": "Name",
                            "type": "string",
                        },
                        "salutation": {
                            "description": "The salutation to use",
                            "title": "Salutation",
                            "type": "string",
                        },
                    },
                    "required": ["name", "salutation"],
                    "title": "Greeting",
                    "type": "object",
                }
            },
            "properties": {
                "greeting": {
                    "allOf": [{"$ref": "#/$defs/Greeting"}],
                    "description": "The greeting to say, and the name to say it to",
                }
            },
            "required": ["greeting"],
            "title": "FunctionParameters",
            "type": "object",
        },
    }


def test_functions_dict_with_pydantic_param_function_call():
    class Greeting(BaseModel):
        name: str = Field(
            ..., description="The name of the person that should be greeted"
        )
        salutation: str = Field(..., description="The salutation to use")

    taifun = Taifun()

    @taifun.fn()
    def hello(greeting: Greeting):
        """
        Say hello

        Parameters
        ----------
        greeting : Greeting
            The greeting to say, and the name to say it to

        """
        return f"{greeting.salutation} {greeting.name}"

    assert (
        taifun.handle_function_call(
            {
                "name": "hello",
                "arguments": json.dumps(
                    {"greeting": {"name": "World", "salutation": "Goodbye"}}
                ),
            }
        )
        == "Goodbye World"
    )


def test_register_fails_if_param_misses_description():
    taifun = Taifun()

    def register_function():
        # this funciton uses wrong format therefore it should fail
        @taifun.fn()
        def hello(name: str):
            """
            Say hello

            Parameters
            ----------
            name(str): The name of the person to say hello to

            """
            return f"Hello {name}"

    pytest.raises(MissingDescriptionError, register_function)
