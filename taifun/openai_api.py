from pydantic import BaseModel
from enum import StrEnum, auto


class Parameter(BaseModel):
    type: str
    description: str | None = None
    enum: list | None = None


class FunctionParameters(BaseModel):
    type: str = "object"
    properties: dict[str, Parameter]
    required: list[str]


class Function(BaseModel):
    name: str
    description: str
    parameters: FunctionParameters


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
    content: str
    function_call: FunctionCall | None = None
