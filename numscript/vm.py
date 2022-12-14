from typing import Any, Dict, List
from numscript.code import Script, Statement
from numscript.errors import ErrorCode, Errors
from numscript.op_codes import Operator
from numscript.object import Object, Type as ObjectType
import time


def check_minimum_arg_number(statement: Statement, expected: int) -> None:
    """
        Statement should never be empty.
        Throw an error if the number of arguments is at least equal to expected.
    """
    if statement.length() < expected + 1:
        Errors.not_enough_arguments(statement.get(0), statement, expected, statement.length() - 1)


def check_exact_arg_number(statement: Statement, expected: int) -> None:
    """
        Statement should never be empty.
        Throw an error if the number of arguments is not equal to expected.
    """
    if statement.length() != expected + 1:
        Errors.invalid_op_arg_number(statement.get(0), statement, expected, statement.length() - 1)


class VM:

    def __init__(self) -> None:
        
        # List of the start addresses of the scopes
        self.scopes: List[int] = [0]
        self.program_counter = 0
        self.stack: List[Object] = []
        self.running = False
        self.script: Script = None
        self.statement: Statement = None
        # Maps label ids to program addresses
        self.labels: Dict[int, int] = {}
        self.goto_stack: List[int] = []
        self.status = ErrorCode.NO_ERROR


    def execute_next_statement(self) -> None:
        self.statement = self.get_next_statement()
        self.execute_statement()


    def get_next_statement(self) -> Statement | None:
        try:            
            line = self.script.statements[self.program_counter]
        except IndexError:
            # The program is finished
            self.running = False
            return None

        self.program_counter += 1
        return line


    def current_scope(self) -> int:
        return self.scopes[-1]


    def current_scope_size(self) -> int:
        return len(self.stack) - self.current_scope()


    def get_stack_address_from_local(self, local_addr: int) -> int:
        # Search the address in the scope stack
        last_scope = len(self.stack)
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
        
        # The address is not in any scope
        Errors.symbol_not_found(local_addr, self.statement)

    
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


    def goto_label(self, label_id: int) -> None:
        if label_id not in self.labels:
            Errors.label_not_found(label_id, self.statement)
        
        # Save the current program counter for later
        self.goto_stack.append(self.program_counter)
        # Perform the jump
        self.program_counter = self.labels[label_id]


    def jump_until_label(self, label_id: int) -> None:
        statement = None
        while True:
            if self.program_counter == len(self.script.statements):
                Errors.label_not_found(label_id, self.statement)
            
            statement = self.get_next_statement()
            if statement.get(0) == Operator.DECLARE_LABEL:
                check_minimum_arg_number(statement, 1)
                if statement.get(1) == label_id:
                    break
            
            self.program_counter += 1
        
        self.labels[label_id] = self.program_counter


    def get_object_value(self, obj: Object, _type: ObjectType) -> Any:
        if obj.type == _type:
            return obj.value
        Errors.invalid_object_type(obj, _type, self.statement)


    def execute_statement(self) -> None:
        if self.statement is None or self.statement.length() == 0:
            return
        
        main_op = self.statement.get(0)
        match main_op:

            case Operator.DECALRE_LOCAL:
                """
                    0 0 [local identifier] [literal int]
                    0 1 [local identifier] [array]
                    0 2 [local identifier] [identifier]
                """                
                check_minimum_arg_number(self.statement, 3)
                
                variant = self.statement.get(1)
                local_dest_id = self.statement.get(2)
                match variant:
                    case 0:
                        check_exact_arg_number(self.statement, 3)
                        value = self.statement.get(3)
                        self.declare_local_object(local_dest_id, Object.from_int(value))                        
                    
                    case 1:
                        array = self.statement.get_from(3)
                        self.declare_local_object(local_dest_id, Object.from_array(array))
                    
                    case 2:
                        check_exact_arg_number(self.statement, 3)
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
                check_minimum_arg_number(self.statement, 3)

                variant = self.statement.get(1)
                dest_id = self.statement.get(2)
                match variant:
                    case 0:
                        check_exact_arg_number(self.statement, 3)
                        value = self.statement.get(3)
                        self.set_object(dest_id, Object.from_int(value))

                    case 1:
                        array = self.statement.get_from(3)
                        self.set_object(dest_id, Object.from_array(array))

                    case 2:
                        check_exact_arg_number(self.statement, 3)
                        src_id = self.statement.get(3)
                        self.set_object(dest_id, self.get_object(src_id))
                    
                    case _:
                        Errors.invalid_op_code_variant(main_op, variant, self.statement)
            
            case Operator.DECLARE_LABEL:
                """
                    2 [label identifier]
                """
                check_exact_arg_number(self.statement, 1)
                label_id = self.statement.get(1)
                self.labels[label_id] = self.program_counter
            
            case Operator.GOTO_LABEL:
                """
                    3 [label identifier]
                """
                check_exact_arg_number(self.statement, 1)
                label_id = self.statement.get(1)
                self.goto_label(label_id)
            
            case Operator.RETURN_FROM_LABEL:
                """
                    4
                """
                check_exact_arg_number(self.statement, 0)
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
                check_exact_arg_number(self.statement, 2)

                variant = self.statement.get(1)
                match variant:
                    case 0:
                        exit_code = self.statement.get(2)
                    
                    case 1:
                        exit_code_id = self.statement.get(2)
                        exit_code_obj = self.get_object(exit_code_id)
                        exit_code = self.get_object_value(exit_code_obj, ObjectType.INT)
                    
                    case _:
                        Errors.invalid_op_code_variant(main_op, variant, self.statement)

                self.running = False
                self.status = exit_code
            
            case Operator.NO_OP:
                """
                    6
                """
                check_exact_arg_number(self.statement, 0)
            
            case Operator.SLEEP_MS:
                """
                    7 0 [literal int]
                    7 1 [identifier]
                """
                check_exact_arg_number(self.statement, 2)

                variant = self.statement.get(1)
                match variant:
                    case 0:
                        sleep_ms = self.statement.get(2)

                    case 1:
                        sleep_ms_id = self.statement.get(2)
                        sleep_ms_obj = self.get_object(sleep_ms_id)
                        sleep_ms = self.get_object_value(sleep_ms_obj, ObjectType.INT)

                    case _:
                        Errors.invalid_op_code_variant(main_op, variant, self.statement)
                        
                time.sleep(sleep_ms / 1000)

            case Operator.PRINT:
                """
                    8 0 [literal int]
                    8 1 [array]
                    8 2 [identifier]
                """
                check_minimum_arg_number(self.statement, 2)

                variant = self.statement.get(1)
                match variant:
                    case 0:
                        check_exact_arg_number(self.statement, 2)
                        value = self.statement.get(2)
                        print(value)

                    case 1:
                        array = self.statement.get_from(2)
                        print(Object.from_array(array).to_string())
                    
                    case 2:
                        check_exact_arg_number(self.statement, 2)
                        src_id = self.statement.get(2)
                        obj = self.get_object(src_id)
                        print(obj.represent())

                    case _:
                        Errors.invalid_op_code_variant(main_op, variant, self.statement)
            
            case Operator.PRINT_STRING:
                """
                    9 0 [int literal]
                    9 1 [array literal]
                    9 2 [identifier]
                """
                check_minimum_arg_number(self.statement, 2)

                variant = self.statement.get(1)
                match variant:
                    case 0:
                        check_exact_arg_number(self.statement, 2)
                        value = self.statement.get(2)
                        print(chr(value))

                    case 1:
                        array = self.statement.get_from(2)
                        print(Object.from_array(array).to_string())

                    case 2:
                        check_exact_arg_number(self.statement, 2)
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
                check_minimum_arg_number(self.statement, 4)

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
                        index = self.get_object_value(index_obj, ObjectType.INT)

                        self.set_object(dest_id, Object.from_int(array[index]))

                    case 2:
                        check_exact_arg_number(self.statement, 4)
                        index = self.statement.get(2)
                        dest_id = self.statement.get(3)
                        array_id = self.statement.get(4)

                        array_obj = self.get_object(array_id)
                        array = self.get_object_value(array_obj, ObjectType.ARRAY)

                        self.set_object(dest_id, Object.from_int(array[index]))

                    case 3:
                        check_exact_arg_number(self.statement, 4)
                        index_id = self.statement.get(2)
                        dest_id = self.statement.get(3)
                        array_id = self.statement.get(4)

                        index_obj = self.get_object(index_id)
                        index = self.get_object_value(index_obj, ObjectType.INT)

                        array_obj = self.get_object(array_id)
                        array = self.get_object_value(array_obj, ObjectType.ARRAY)

                        self.set_object(dest_id, Object.from_int(array[index]))

            case Operator.IF_JUMP:
                """
                    11 0 [literal condition] [label]
                    11 1 [identifier condition] [label]
                    11 2 [literal condition] [stop label]
                    11 3 [identifier condition] [stop label]
                """
                check_exact_arg_number(self.statement, 3)

                variant = self.statement.get(1)
                match variant:
                    case 0:
                        condition = self.statement.get(2)
                        label_id = self.statement.get(3)
                        if condition:
                            self.goto_label(label_id)
                        
                    case 1:
                        condition_id = self.statement.get(2)
                        label_id = self.statement.get(3)
                        condition_obj = self.get_object(condition_id)
                        condition = self.get_object_value(condition_obj, ObjectType.BOOL)
                        if condition:
                            self.goto_label(label_id)
                        
                    case 2:
                        condition = self.statement.get(2)
                        label_id = self.statement.get(3)
                        if condition:
                            self.jump_until_label(label_id)
                        
                    case 3:
                        condition_id = self.statement.get(2)
                        label_id = self.statement.get(3)
                        condition_obj = self.get_object(condition_id)
                        condition = self.get_object_value(condition_obj, ObjectType.BOOL)
                        if condition:
                            self.jump_until_label(label_id)

            case Operator.INPUT:
                """
                    12 0 [save address] # input int
                    12 1 [save address] # input array
                    12 2 [save address] # input char as int
                    12 3 [save address] # input string as array
                """
                check_exact_arg_number(self.statement, 2)

                variant = self.statement.get(1)
                dest_id = self.statement.get(2)
                try:
                    match variant:
                        case 0:
                            int_input = int(input())  
                            self.set_object(dest_id, Object.from_int(int_input))
                        
                        case 1:
                            array_input = [int(c) for c in input().split(' ')]
                            self.set_object(dest_id, Object.from_array(array_input))
                        
                        case 2:
                            int_input = ord(input())
                            self.set_object(dest_id, Object.from_int(int_input))

                        case 3:
                            array_input = [ord(c) for c in input()]
                            self.set_object(dest_id, Object.from_array(array_input))
                            
                except ValueError:
                    self.status = ErrorCode.INVALID_INPUT
                    return
                except TypeError:
                    self.status = ErrorCode.INVALID_INPUT
                    return
                except EOFError:
                    self.status = ErrorCode.EOF
                    return

            case _:
                Errors.invalid_op_code(main_op, self.statement)



    def run(self, script: Script) -> ErrorCode:
        self.script = script
        self.running = True
        while self.running:
            self.execute_next_statement()
        
        return self.status
            
