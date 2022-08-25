from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class Statement:
    line_number: int
    tokens: Tuple[int]

    def get(self, index: int) -> int:
        return self.tokens[index]
    
    def get_from(self, index: int) -> Tuple[int]:
        return self.tokens[index:]
    
    def length(self) -> int:
        return len(self.tokens)


@dataclass
class Script:
    statements: Tuple[Statement]

    
def parse(script: str) -> Script:
    lines = enumerate(script.splitlines(), start=1)
    statements: List[Statement] = []

    for line_number, line in lines:
        if line == '':
            statements.append(Statement(line_number, ()))
        else:
            statement = tuple(map(int, line.split(' ')))
            statements.append(Statement(line_number, statement))

    return Script(tuple(statements))
            
