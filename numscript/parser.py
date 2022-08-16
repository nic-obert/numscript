from typing import Tuple
from dataclasses import dataclass


@dataclass
class Statement:
    line_number: int
    tokens: Tuple[int]


@dataclass
class Script:
    statements: Tuple[Statement]

    
def parse(script: str) -> Script:
    return Script(
        statements=tuple(
            Statement(
                line_number,
                tuple(int(token) for token in statement)
            ) for line_number, statement in enumerate(script)
        )
    )

