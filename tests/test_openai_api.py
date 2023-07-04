from pydantic import TypeAdapter

from taifun.openai_api import (Function, FunctionCall, FunctionParameters,
                               Message, Parameter, Role)


def test_messages_model():
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "You are a task assistant."},
        {
            "role": "function",
            "content": "",
            "function_call": {"name": "hello", "arguments": ""},
        },
        
    ]

    assert TypeAdapter(list[Message]).validate_python(messages) == [
        Message(role=Role.system, content="You are a helpful assistant."),
        Message(role=Role.user, content="Hello!"),
        Message(role=Role.assistant, content="You are a task assistant."),
        Message(role=Role.function, content="", function_call=FunctionCall(name="hello", arguments="")),

    ]


def test_functions_model():
    functions = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        }
    ]

    assert TypeAdapter(list[Function]).validate_python(functions) == [
        Function(
            name="get_current_weather",
            description="Get the current weather in a given location",
            parameters=FunctionParameters(
                type="object",
                properties={
                    "location": Parameter(
                        type="string",
                        description="The city and state, e.g. San Francisco, CA",
                    ),
                    "unit": Parameter(type="string", enum=["celsius", "fahrenheit"]),
                },
                required=["location"],
            ),
        )
    ]
