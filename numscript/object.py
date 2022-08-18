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
