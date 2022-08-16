from numscript.parser import Script, Statement
from numscript.errors import ErrorCode, Errors
from numscript.op_codes import Operator


def check_arg_number(statement: Statement, expected: int) -> None:
    """
        Statement should never be empty.
        Throw an error if the number of arguments is not equal to expected.
    """
    # -1 to account for the main operation token
    if len(statement.tokens) - 1 != expected:
        Errors.invalid_op_arg_number(statement.tokens[0], statement, expected, len(statement.tokens) - 1)


class VM:

    def __init__(self) -> None:
        self.stack_pointer = 0
        self.program_counter = 0
        self.stack = []
        self.running = False


    def getStatement(self, script: Script) -> Statement:
        line = script.statements[self.program_counter]
        self.program_counter += 1
        return line


    def execute(self, statement: Statement) -> None:
        if len(statement) == 0:
            return
        
        main_op = statement[0]
        match main_op:

            case Operator.SET_ADDRESS:
                """
                    0 0 [relative stack address (to stack pointer)] [literal value]
                    0 1 [relative stack address] [relative stack address]
                """                
                check_arg_number(statement, 3)
                
                variant = statement[1]
                if variant == 0:
                    stack_address = statement[2]
                    value = statement[3]
                    # TODO: finish
                


    def run(self, script: Script) -> ErrorCode:
        self.running = True
        while self.running:
            statement = self.getStatement(script)
            self.execute(statement)

            
