from pydantic import BaseModel
from enum import StrEnum, auto


class Function(BaseModel):
    name: str
    description: str
    parameters: dict


class Role(StrEnum):
    system = auto()
    user = auto()
    function = auto()
    assistant = auto()


class FunctionCall(BaseModel):
    name: str
    arguments: str


class Message(BaseModel):
    role: Role
    content: str = ""
    name: str | None = None
    function_call: FunctionCall | None = None
