from pydantic import TypeAdapter

from taifun.openai_api import FunctionCall, Message, Role


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
        Message(
            role=Role.function,
            content="",
            function_call=FunctionCall(name="hello", arguments=""),
        ),
    ]
