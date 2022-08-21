# NumScript

An esoteric structured programming language that only uses numbers.

- [NumScript](#numscript)
- [Usage](#usage)
- [License](#license)
- [Documentation](#documentation)
  - [Operators](#operators)
    - [0 - Declare local variable](#0---declare-local-variable)
    - [1 - Set variable](#1---set-variable)
    - [2 - Declare label](#2---declare-label)
    - [3 - Goto label](#3---goto-label)
    - [4 - Return from label](#4---return-from-label)
    - [5 - Exit the program](#5---exit-the-program)
    - [6 - No operation](#6---no-operation)
    - [7 - Sleep milliseconds](#7---sleep-milliseconds)
    - [8 - Print](#8---print)
    - [9 - Print as string](#9---print-as-string)
    - [10 - Access array element at index](#10---access-array-element-at-index)
    - [11 - If jump](#11---if-jump)

# Usage

Execute a NumScript program

    $ numscript <file.ns>

# License

All the files included in this repository are distributed under the [MIT license](LICENSE).

# Documentation

NumScript is a strictly-structured programming language whose statements are composed of
a main operator, an optional operator variant, and a sequence of operands.  
Basic statement structure:
```
    <main operator> <optional variant> <args>...
```

## Operators

Operators are identified by an unsigned integer number.

### 0 - Declare local variable
Declare a local variable.  
Variants:
- `0 0 [local identifier] [literal int]`  
    Declare a local variable at the given local scope index with the given literal integer value.
- `0 1 [local identifier] [literal array]`  
    Declare a local variable at the given local scope index with the given array value.
- `0 2 [local identifier] [identifier]`  
    Declare a local variable at the given local scope index with the value of the given identifier.

### 1 - Set variable
Set the value of a reachable variable.  
Variants:
- `1 0 [identifier] [literal int]`  
    Set the value of the given variable to the given literal integer value.
- `1 1 [identifier] [literal array]`  
    Set the value of the given variable to the given array value.
- `1 2 [identifier] [identifier]`  
    Set the value of the given variable to the value of the given identifier.

### 2 - Declare label
Declare a named label pointing to the current statement identified by the VM program counter (the statement right after the label declaration).
- `2 [label integer identifier]`

### 3 - Goto label
Jump to the statement identified by the given label.
- `3 [label integer identifier]`
  
### 4 - Return from label
Return from the last go-to-label.
- `4`
  
### 5 - Exit the program
Exit the program with the given integer exit code.  
Variants:
- `5 0 [literal int exit code]`  
    Exit with the given literal int exit code.
- `5 1 [identifier exit code]`  
    Exit with the value of the given identifier exit code.

### 6 - No operation
Do nothing.
- `6`

### 7 - Sleep milliseconds
Sleep for the given number of milliseconds.  
Variants:
- `7 0 [literal int milliseconds]`  
    Sleep for the given literal int milliseconds.
- `7 1 [identifier milliseconds]`  
    Sleep for the value of the given identifier milliseconds.

### 8 - Print
Print the given value to the console.  
Variants:
- `8 0 [literal int]`  
    Print the given literal int to the console.
- `8 1 [literal array]`  
    Print the given literal array to the console.
- `8 2 [identifier]`  
    Print the value of the given identifier to the console.

### 9 - Print as string
Print the given value as a string to the console.  
Variants:
- `9 0 [literal int]`    
    Print the given literal int as a string to the console.
- `9 1 [literal array]`  
    Print the given literal array as a string to the console.
- `9 2 [identifier]`  
    Print the value of the given identifier as a string to the console.

### 10 - Access array element at index
Access the array element at the given integer index.  
Variants:
- `10 0 [literal int index] [dest address] [literal array]`  
    Access the literal array element at the given literal int index and store it at the given literal array address.
- `10 1 [identifier int index] [dest address] [literal array]`  
    Access the literal array element at the value of the given identifier int index and store it at the given literal array address.
- `10 2 [literal int index] [dest address] [identifier array]`  
    Access the literal array element at the given literal int index and store it at the value of the given identifier array address.
- `10 3 [identifier int index] [dest address] [identifier array]`  
    Access the literal array element at the value of the given identifier int index and store it at the value of the given identifier array address.

### 11 - If jump
Jump to the given statement if the given condition is true.  
Variants:
- `11 0 [literal condition] [label integer identifier]`  
    Jump to the statement identified by the given label if the given literal condition is true.
- `11 1 [identifier condition] [label integer identifier]`  
    Jump to the statement identified by the given label if the value of the given identifier condition is true.
- `11 2 [literal condition] [stop label]`  
    Jump to the statement following the stop label if the condition is true. The stop label must be found after the if-jump statement.
- `11 3 [identifier condition] [stop label]`  
    Jump to the statement following the stop label if the value of the given identifier condition is true. The stop label must be found after the if-jump statement.




