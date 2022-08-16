from enum import IntEnum
from typing import Any
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
    def invalid_op_arg_number(operation: Operator, statement: Statement, expected: int, got: int) -> None:
        Errors.error(f"""
            Invalid argument number for operation {operation} on line {statement.line_number}.
            Expected {expected} arguments, got {got}:
            {statement.tokens}
        """)

