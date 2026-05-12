from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

@dataclass
class VmArithmeticTranslator:
    def translate(self, line: str) -> Iterable[str]:

        asm = None
        match line:
            case "add":
                asm = vm_add()
            case "sub":
                asm = vm_sub()
            # case "eq":
            #     asm = vm_eq()
            # case "gt":
            #     asm = vm_gt()
            # case "lt":
            #     asm = vm_lt()
            case "neg":
                asm = vm_neg()
            case "and":
                asm = vm_and()
            case "or":
                asm =  vm_or()
            case "not":
                asm = vm_not()
            case _:
                raise Exception(f"Command <{line}> not found")

        return asm.splitlines()

def vm_add() -> str:
    return """
        // add
        @SP
        AM=M-1
        D=M
        A=A-1
        M=M+D
    """

def vm_sub() -> str:
    return """
        // sub
        @SP
        AM=M-1
        D=M
        A=A-1
        M=M-D
    """

def vm_eq() -> str:
    return """
        // eq
        @SP
        AM=M-1
        D=M
        A=A-1
        MD=M-D

        @EQ
        D; JEQ
        @NEQ
        0; JMP

        (EQ)
        @SP
        A=M-1
        M=-1
        @CONT
        0; JMP

        (NEQ)
        @SP
        A=M-1
        M=0

        (CONT)
    """

def vm_gt() -> str:
    return """
        // gt
        @SP
        AM=M-1
        D=M
        A=A-1
        MD=M-D

        @GT
        D; JGT
        @LE
        0; JMP

        (GT)
        @SP
        A=M-1
        M=-1
        @CONT
        0; JMP

        (LE)
        @SP
        A=M-1
        M=0

        (CONT)
    """

def vm_lt() -> str:
    return """
        // lt
        @SP
        AM=M-1
        D=M
        A=A-1
        MD=M-D

        @GE
        D; JGE
        @LTE
        0; JMP

        (GE)
        @SP
        A=M-1
        M=0
        @CONT
        0; JMP

        (LE)
        @SP
        A=M-1
        M=-1

        (CONT)
    """

def vm_neg() -> str:
    return """
        // neg
        @SP
        A=M-1
        M=-M
    """

def vm_and() -> str:
    return """
        // and
        @SP
        AM=M-1
        D=M
        A=A-1
        M=M&D
    """

def vm_or() -> str:
    return """
        // or
        @SP
        AM=M-1
        D=M
        A=A-1
        M=M|D
    """

def vm_not() -> str:
    return """
        // not
        @SP
        A=M
        M=!M
    """
