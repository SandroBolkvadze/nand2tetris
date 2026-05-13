from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

_BRANCH_COMMANDS = [
    "goto",
    "if-goto",
]


@dataclass
class VmBranchTranslator:
    filename: str

    def translate(self, line: str) -> Iterable[str]:
        command, label = line.split()
        asm = None

        match command:
            case "goto":
                asm = vm_goto(self.filename, label)
            case "if-goto":
                asm = vm_if_goto(self.filename, label)
            case _:
                raise Exception(f"Unknown Branch command <{line}>")

        return [token.strip() for token in asm.splitlines() if len(token)]


def vm_goto(filename: str, label: str) -> str:
    return f"""
        @{filename}.{label}
        0; JMP
    """


def vm_if_goto(filename: str, label: str) -> str:
    return f"""
        @SP
        AM=M-1
        D=M
        @{filename}.{label}
        D; JNE
    """
