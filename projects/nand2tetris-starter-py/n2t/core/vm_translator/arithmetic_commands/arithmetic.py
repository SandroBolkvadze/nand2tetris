from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from n2t.core.vm_translator.utils.state import VmTranslatorState

ARITHMETIC_COMMANDS = [
    "add",
    "sub",
    "neg",
    "eq",
    "gt",
    "lt",
    "and",
    "or",
    "not",
]


@dataclass
class VmArithmeticTranslator:
    state: VmTranslatorState

    def translate(self, line: str) -> Iterable[str]:

        asm = None
        match line:
            case "add":
                asm = vm_add()
            case "sub":
                asm = vm_sub()
            case "eq":
                self.state.total_eq_count += 1
                asm = vm_eq(self.state.filename, self.state.total_eq_count)
            case "gt":
                self.state.total_gt_count += 1
                asm = vm_gt(self.state.filename, self.state.total_gt_count)
            case "lt":
                self.state.total_lt_count += 1
                asm = vm_lt(self.state.filename, self.state.total_lt_count)
            case "neg":
                asm = vm_neg()
            case "and":
                asm = vm_and()
            case "or":
                asm = vm_or()
            case "not":
                asm = vm_not()
            case _:
                raise Exception(f"Command <{line}> not found")

        return [token.strip() for token in asm.splitlines() if len(token)]


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


def vm_eq(filename: str, eq_count: int) -> str:
    eq_label = f"{filename}$eq.{eq_count}"
    neq_label = f"{filename}$neq.{eq_count}"

    return f"""
        // eq
        @SP
        AM=M-1
        D=M
        A=A-1
        D=M-D
        M=0

        @{eq_label}
        D; JEQ
        @{neq_label}
        0; JMP

        ({eq_label})
        @SP
        A=M-1
        M=-1

        ({neq_label})
    """


def vm_gt(filename: str, gt_count: int) -> str:
    gt_label = f"{filename}$gt.{gt_count}"
    le_label = f"{filename}$le.{gt_count}"

    return f"""
        // gt
        @SP
        AM=M-1
        D=M
        A=A-1
        D=M-D
        M=0

        @{gt_label}
        D; JGT
        @{le_label}
        0; JMP

        ({gt_label})
        @SP
        A=M-1
        M=-1

        ({le_label})
    """


def vm_lt(filename: str, lt_count: int) -> str:
    lt_label = f"{filename}$lt.{lt_count}"
    ge_label = f"{filename}$ge.{lt_count}"

    return f"""
        // lt
        @SP
        AM=M-1
        D=M
        A=A-1
        D=M-D
        M=0

        @{lt_label}
        D; JLT
        @{ge_label}
        0; JMP

        ({lt_label})
        @SP
        A=M-1
        M=-1

        ({ge_label})
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
        A=M-1
        M=!M
    """
