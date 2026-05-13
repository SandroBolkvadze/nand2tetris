from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class VmPopTranslator:
    filename: str

    def translate(self, line: str) -> Iterable[str]:
        tokens = line.split()
        segment, index = tokens[1], int(tokens[2])

        asm = None
        match segment:
            case "local":
                asm = pop_local(index)
            case "argument":
                asm = pop_argument(index)
            case "this":
                asm = pop_this(index)
            case "that":
                asm = pop_that(index)
            case "static":
                asm = pop_static(self.filename, index)
            case "temp":
                asm = pop_temp(index)
            case "pointer":
                asm = pop_pointer(index)
            case _:
                raise Exception(f"Unknown command <{line}>")

        return asm.splitlines()


def pop_local(i: int) -> str:
    return f"""
        // pop local
        @{i}
        D=A
        @LCL
        D=M+D
        @R13
        M=D
        @SP
        AM=M-1
        D=M
        @R13
        A=M
        M=D
    """


def pop_argument(i: int) -> str:
    return f"""
        // pop argument
        @{i}
        D=A
        @ARG
        D=M+D
        @R13
        M=D
        @SP
        AM=M-1
        D=M
        @R13
        A=M
        M=D
    """


def pop_this(i: int) -> str:
    return f"""
        // pop this
        @{i}
        D=A
        @THIS
        D=M+D
        @R13
        M=D
        @SP
        AM=M-1
        D=M
        @R13
        A=M
        M=D
    """


def pop_that(i: int) -> str:
    return f"""
        // pop that
        @{i}
        D=A
        @THAT
        D=M+D
        @R13
        M=D
        @SP
        AM=M-1
        D=M
        @R13
        A=M
        M=D
    """


def pop_static(prefix: str, i: int):
    return f"""
        // pop static
        @SP
        AM=M-1
        D=M
        @{prefix}.{i}
        M=D
    """


def pop_temp(i: int):
    return f"""
        // pop temp
        @{i}
        D=A
        @{5}
        D=D+A
        @R13
        M=D
        @SP
        AM=M-1
        D=M
        @R13
        A=M
        M=D
    """


def pop_pointer(i: int):
    return f"""
        // pop pointer
        @{i}
        D=A
        @{3}
        D=D+A
        @R13
        M=D
        @SP
        AM=M-1
        D=M
        @R13
        A=M
        M=D
    """
