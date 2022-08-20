from enum import IntEnum
from typing import Any
from numscript.object import Object, Type as ObjectType
from numscript.op_codes import Operator
from numscript.parser import Statement
from sys import stderr


class ErrorCode(IntEnum):

    NO_ERROR = 0


class Errors:

    @staticmethod
    def error(*args: Any) -> None:
        print(*args, file=stderr)
        exit(1)

    @staticmethod
    def invalid_op_arg_number(operator: Operator, statement: Statement, expected: int, got: int) -> None:
        Errors.error(f"""
            Invalid argument number for operation {operator} on line {statement.line_number}.
            Expected {expected} arguments, got {got}:
            {statement.tokens}
        """)

    @staticmethod
    def invalid_op_code(operator: Operator, statement: Statement) -> None:
        Errors.error(f"""
            Invalid operation code {operator} on line {statement.line_number}:
            {statement.tokens}
        """)
    
    @staticmethod
    def symbol_redeclaration(identifier: int, statement: Statement) -> None:
        Errors.error(f"""
            Symbol {identifier} redeclared on line {statement.line_number}:
            {statement.tokens}
        """)
    
    @staticmethod
    def invalid_op_code_variant(operator: Operator, variant: int, statement: Statement) -> None:
        Errors.error(f"""
            Invalid operation code variation {variant} for operator {operator} on line {statement.line_number}:
            {statement.tokens}
        """)

    @staticmethod
    def label_not_found(label: int, statement: Statement) -> None:
        Errors.error(f"""
            Label {label} not found on line {statement.line_number}:
            {statement.tokens}
        """)
    
    @staticmethod
    def no_label_to_return_from(statement: Statement) -> None:
        Errors.error(f"""
            No label to return from on line {statement.line_number}:
            {statement.tokens}
        """)
    
    @staticmethod
    def no_string_representation(object: Object, statement: Statement) -> None:
        Errors.error(f"""
            No string representation for object {object} on line {statement.line_number}:
            {statement.tokens}
        """)
    
    @staticmethod
    def invalid_object_type(object: Object, expected_type: ObjectType, statement: Statement) -> None:
        Errors.error(f"""
            Invalid index type for object {object} (expected {expected_type}) on line {statement.line_number}:
            {statement.tokens}
        """)
