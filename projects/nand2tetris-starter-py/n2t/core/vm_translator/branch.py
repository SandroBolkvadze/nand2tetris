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
                asm = f"""
                    @{self.filename}.{label}
                    0; JMP
                """
            case "if-goto":
                asm = f"""
                    @SP
                    AM=M-1
                    D=M
                    @{self.filename}.{label}
                    D; JNE
                """
            case _:
                raise Exception(f"Unknown Branch command <{line}>")

        return asm.splitlines()
