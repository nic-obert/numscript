#!/usr/bin/env python3
from sys import argv


def str_to_num(s: str):
    return [ord(c) for c in s]


if __name__ == '__main__':
    nums = str_to_num(argv[1])
    for n in nums:
        print(n, end=' ')
    print()
