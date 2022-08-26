from dataclasses import dataclass
from typing import Tuple


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

