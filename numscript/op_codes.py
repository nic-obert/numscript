from enum import IntEnum


class Operator(IntEnum):

    DECALRE_LOCAL = 0
    SET = 1
    DECLARE_LABEL = 2
    GOTO_LABEL = 3
    RETURN_FROM_LABEL = 4
    EXIT = 5
    NO_OP = 6
    SLEEP_MS = 7
    PRINT = 8
    PRINT_STRING = 9
    ACCESS_INDEX = 10

    
    # IF_CHECK = 
    

