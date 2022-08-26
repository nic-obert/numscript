from typing import List
from numscript.errors import Errors
from numscript.code import Statement, Script

    
def parse(script: str) -> Script:
    lines = enumerate(script.splitlines(), start=1)
    statements: List[Statement] = []

    for line_number, line in lines:
        if line == '':
            statements.append(Statement(line_number, ()))
        else:
            statement = []
            for token in line.split(' '):
                if token == '':
                    continue
                try:
                    statement.append(int(token))
                except ValueError:
                    Errors.invalid_token(token, line, line_number)

            statements.append(Statement(line_number, statement))

    return Script(tuple(statements))
            
