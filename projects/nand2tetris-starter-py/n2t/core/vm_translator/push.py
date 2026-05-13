from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class VmPushTranslator:
    filename: str

    def translate(self, line: str) -> Iterable[str]:
        tokens = line.split()
        segment, index = tokens[1], int(tokens[2])

        asm = None
        match segment:
            case "constant":
                asm = push_constant(index)
            case "local":
                asm = push_local(index)
            case "argument":
                asm = push_argument(index)
            case "this":
                asm = push_this(index)
            case "that":
                asm = push_that(index)
            case "static":
                asm = push_static(self.filename, index)
            case "temp":
                asm = push_temp(index)
            case "pointer":
                asm = push_pointer(index)
            case _:
                raise Exception(f"Unknown command <{line}>")

        return asm.splitlines()


def push_constant(i: int) -> str:
    return f"""
        // push constant
        @{i}
        D=A
        {push_d()}
    """


def push_local(i: int) -> str:
    return f"""
        // push local
        @{i}
        D=A
        @LCL
        A=M+D
        D=M
        {push_d()}
    """


def push_argument(i: int) -> str:
    return f"""
        // push argument
        @{i}
        D=A
        @ARG
        A=M+D
        D=M
        {push_d()}
    """


def push_this(i: int) -> str:
    return f"""
        // push this
        @{i}
        D=A
        @THIS
        A=M+D
        D=M
        {push_d()}
    """


def push_that(i: int) -> str:
    return f"""
        // push that
        @{i}
        D=A
        @THAT
        A=M+D
        D=M
        {push_d()}
    """


def push_static(prefix: str, i: int):
    return f"""
        // push static
        @{i}
        D=A
        @{prefix}.{i}
        D=M
        {push_d()}
    """


def push_temp(i: int):
    return f"""
        // push temp
        @{i}
        D=A
        @{5}
        A=A+D
        D=M
        {push_d()}
    """


def push_pointer(i: int):
    return f"""
        // push pointer
        @{i}
        D=A
        @{3}
        A=D+A
        D=M
        {push_d()}
    """


def push_d():
    return """
        // push D
        @SP
        M=M+1
        A=M-1
        M=D
    """
