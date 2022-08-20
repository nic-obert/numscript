from typing import Dict, List
from numscript.parser import Script, Statement
from numscript.errors import ErrorCode, Errors
from numscript.op_codes import Operator
from numscript.object import Object, Type as ObjectType
import time


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
        
        # List of the start addresses of the scopes
        self.scopes: List[int] = []
        self.program_counter = 0
        self.stack: List[Object] = []
        self.running = False
        self.statement: Statement | None = None
        # Maps label ids to program addresses
        self.labels: Dict[int, int] = {}
        self.goto_stack: List[int] = []
        self.status = ErrorCode.NO_ERROR


    def execute_next_statement(self, script: Script) -> None:
        self.statement = self.get_next_statement(script)
        self.execute_statement()


    def get_next_statement(self, script: Script) -> Statement:
        line = script.statements[self.program_counter]
        self.program_counter += 1
        return line


    def current_scope(self) -> int:
        return self.scopes[-1]


    def current_scope_size(self) -> int:
        return len(self.stack) - self.current_scope()


    def get_stack_address_from_local(self, local_addr: int) -> int:
        # Search the address in the scope stack
        last_scope = self.current_scope()
        for scope in reversed(self.scopes):
            # Check if the scope contains the address
            # Get the size of the scope
            size = last_scope - scope
            if local_addr >= size:
                # The address is not in the scope
                # Continue searching in the previous scope
                last_scope = scope
                continue

            # The address is in the scope
            return scope + local_addr

    
    def get_object(self, local_addr: int) -> Object:
        return self.stack[self.get_stack_address_from_local(local_addr)]
    

    def set_object(self, local_addr: int, obj: Object) -> None:
        self.stack[self.get_stack_address_from_local(local_addr)] = obj


    def declare_local_object(self, address: int, obj: Object) -> None:
        # Check if the address is already taken in the local scope
        if self.current_scope_size() > address:
            Errors.symbol_redeclaration(address, self.statement)
        
        # Add the object to the local scope
        self.stack.append(obj)

    
    def set_local_object(self, address: int, obj: Object) -> None:
        self.stack[self.current_scope() + address] = obj
    

    def get_local_object(self, address: int) -> Object:
        return self.stack[self.current_scope() + address]


    def execute_statement(self) -> None:
        if self.statement.length() == 0:
            return
        
        main_op = self.statement.get(0)
        match main_op:

            case Operator.DECALRE_LOCAL:
                """
                    0 0 [local identifier] [literal int]
                    0 1 [local identifier] [array]
                    0 2 [local identifier] [identifier]
                """                
                check_arg_number(self.statement, 3)
                
                variant = self.statement.get(1)
                local_dest_id = self.statement.get(2)
                match variant:
                    case 0:
                        value = self.statement.get(3)
                        self.declare_local_object(local_dest_id, Object.from_int(value))                        
                    
                    case 1:
                        array = self.statement.get_from(3)
                        self.declare_local_object(local_dest_id, Object.from_array(array))
                    
                    case 2:
                        src_id = self.statement.get(3)
                        self.declare_local_object(local_dest_id, self.get_object(src_id))
                    
                    case _:
                        Errors.invalid_op_code_variant(main_op, variant, self.statement)
            
            case Operator.SET:
                """
                    1 0 [identifier] [literal int]
                    1 1 [identifier] [array]
                    1 2 [identifier] [identifier]
                """
                check_arg_number(self.statement, 3)

                variant = self.statement.get(1)
                dest_id = self.statement.get(2)
                match variant:
                    case 0:
                        value = self.statement.get(3)
                        self.set_object(dest_id, Object.from_int(value))

                    case 1:
                        array = self.statement.get_from(3)
                        self.set_object(dest_id, Object.from_array(array))

                    case 2:
                        src_id = self.statement.get(3)
                        self.set_object(dest_id, self.get_object(src_id))
                    
                    case _:
                        Errors.invalid_op_code_variant(main_op, variant, self.statement)
            
            case Operator.DECLARE_LABEL:
                """
                    2 [label identifier]
                """
                check_arg_number(self.statement, 1)
                label_id = self.statement.get(1)
                self.labels[label_id] = self.program_counter
            
            case Operator.GOTO_LABEL:
                """
                    3 [label identifier]
                """
                check_arg_number(self.statement, 1)
                label_id = self.statement.get(1)
                if label_id not in self.labels:
                    Errors.label_not_found(label_id, self.statement)
                
                # Save the current program counter for later
                self.goto_stack.append(self.program_counter)
                # Perform the jump
                self.program_counter = self.labels[label_id]
            
            case Operator.RETURN_FROM_LABEL:
                """
                    4
                """
                check_arg_number(self.statement, 0)
                # Restore the program counter
                try:
                    self.program_counter = self.goto_stack.pop()
                except IndexError:
                    Errors.no_label_to_return_from(self.statement)
            
            case Operator.EXIT:
                """
                    5 0 [literal int]
                    5 1 [identifier]
                """
                check_arg_number(self.statement, 2)

                variant = self.statement.get(1)
                match variant:
                    case 0:
                        exit_code = self.statement.get(2)
                    
                    case 1:
                        exit_code_id = self.statement.get(2)
                        exit_code_obj = self.get_object(exit_code_id)

                        if exit_code_obj.type != ObjectType.INT:
                            Errors.invalid_object_type(exit_code_obj.type, ObjectType.INT, self.statement)
                        exit_code = exit_code_obj.value
                    
                    case _:
                        Errors.invalid_op_code_variant(main_op, variant, self.statement)

                self.running = False
                self.status = exit_code
            
            case Operator.NO_OP:
                """
                    6
                """
                check_arg_number(self.statement, 0)
            
            case Operator.SLEEP_MS:
                """
                    7 0 [literal int]
                    7 1 [identifier]
                """
                check_arg_number(self.statement, 2)

                variant = self.statement.get(1)
                match variant:
                    case 0:
                        sleep_ms = self.statement.get(2)

                    case 1:
                        sleep_ms_id = self.statement.get(2)
                        sleep_ms_obj = self.get_object(sleep_ms_id)

                        if sleep_ms_obj.type != ObjectType.INT:
                            Errors.invalid_object_type(sleep_ms_obj.type, ObjectType.INT, self.statement)
                        sleep_ms = sleep_ms_obj.value

                    case _:
                        Errors.invalid_op_code_variant(main_op, variant, self.statement)
                        
                time.sleep(sleep_ms / 1000)

            case Operator.PRINT:
                """
                    8 0 [literal int]
                    8 1 [array]
                    8 2 [identifier]
                """
                check_arg_number(self.statement, 2)

                variant = self.statement.get(1)
                match variant:
                    case 0:
                        value = self.statement.get(2)
                        print(value)

                    case 1:
                        array = self.statement.get_from(2)
                        print(array)
                    
                    case 2:
                        src_id = self.statement.get(2)
                        print(self.get_object(src_id))
                    
                    case _:
                        Errors.invalid_op_code_variant(main_op, variant, self.statement)
            
            case Operator.PRINT_STRING:
                """
                    9 0 [int literal]
                    9 1 [array literal]
                    9 2 [identifier]
                """
                check_arg_number(self.statement, 2)

                variant = self.statement.get(1)
                match variant:
                    case 0:
                        value = self.statement.get(2)
                        print(chr(value))

                    case 1:
                        array = self.statement.get_from(2)
                        print(''.join(chr(c) for c in array))

                    case 2:
                        src_id = self.statement.get(2)
                        obj = self.get_object(src_id)
                        string = obj.to_string()
                        if string is None:
                            Errors.no_string_representation(obj, self.statement)
                        print(string)

            case Operator.ACCESS_INDEX:
                """
                    10 0 [literal int index] [save address] [literal array]
                    10 1 [identifier index] [save address] [literal array]
                    10 2 [literal int index] [save address] [identifier array]
                    10 3 [identifier index] [save address] [identifier array]
                """
                check_arg_number(self.statement, 4)

                variant = self.statement.get(1)
                match variant:
                    case 0:
                        index = self.statement.get(2)
                        dest_id = self.statement.get(3)
                        array = self.statement.get_from(4)
                        self.set_object(dest_id, Object.from_int(array[index]))
                        
                    case 1:
                        index_id = self.statement.get(2)
                        dest_id = self.statement.get(3)
                        array = self.statement.get_from(4)

                        index_obj = self.get_object(index_id)
                        if index_obj.type != ObjectType.INT:
                            Errors.invalid_object_type(index_obj, ObjectType.INT, self.statement)
                        index = index_obj.value

                        self.set_object(dest_id, Object.from_int(array[index]))

                    case 2:
                        index = self.statement.get(2)
                        dest_id = self.statement.get(3)
                        array_id = self.statement.get(4)

                        array_obj = self.get_object(array_id)
                        if array_obj.type != ObjectType.ARRAY:
                            Errors.invalid_object_type(array_obj, ObjectType.ARRAY, self.statement)
                        array = array_obj.value

                        self.set_object(dest_id, Object.from_int(array[index]))

                    case 3:
                        index_id = self.statement.get(2)
                        dest_id = self.statement.get(3)
                        array_id = self.statement.get(4)

                        index_obj = self.get_object(index_id)
                        if index_obj.type != ObjectType.INT:
                            Errors.invalid_object_type(index_obj, ObjectType.INT, self.statement)
                        index = index_obj.value

                        array_obj = self.get_object(array_id)
                        if array_obj.type != ObjectType.ARRAY:
                            Errors.invalid_object_type(array_obj, ObjectType.ARRAY, self.statement)
                        array = array_obj.value

                        self.set_object(dest_id, Object.from_int(array[index]))


            case _:
                Errors.invalid_op_code(main_op, self.statement)



    def run(self, script: Script) -> ErrorCode:
        self.running = True
        while self.running:
            self.execute_next_statement(script)
        
        return self.status
            
