from __future__ import annotations
from typing import Any
from enum import IntEnum


class Type(IntEnum):

    INT = 0
    ARRAY = 1


class Object():
    
    def __init__(self, value: Any, _type: Type) -> None:
        self.value = value
        self.type = _type

    
    @staticmethod
    def from_int(value: int) -> Object:
        return Object(value, Type.INT)
    

    @staticmethod
    def from_array(value: list) -> Object:
        return Object(value, Type.ARRAY)
    

    def to_string(self) -> str | None:
        match self.type:
            case Type.INT:
                return chr(self.value)
            case Type.ARRAY:
                return ''.join(chr(x) for x in self.value)
            case _:
                return None
    

    def represent(self) -> str:
        match self.type:
            case Type.INT:
                return str(self.value)
            case Type.ARRAY:
                return ' '.join(str(x) for x in self.value)
            case _:
                return f"<Object {self.type}: {self.value}>"
                
