from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from n2t.core.vm_translator.utils.state import VmTranslatorState

BRANCH_COMMANDS = [
    "goto",
    "if-goto",
]


@dataclass
class VmBranchTranslator:
    state: VmTranslatorState

    def translate(self, line: str) -> Iterable[str]:
        command, label = line.split()
        asm = None

        match command:
            case "goto":
                asm = vm_goto(self.state.filename, self.state.current_function, label)
            case "if-goto":
                asm = vm_if_goto(
                    self.state.filename, self.state.current_function, label
                )
            case _:
                raise Exception(f"Unknown Branch command <{line}>")

        return [line.strip() for line in asm.splitlines() if len(line)]


def vm_goto(filename: str, current_function: str, label: str) -> str:
    return f"""
        @{filename}.{current_function}${label}
        0; JMP
    """


def vm_if_goto(filename: str, current_function: str, label: str) -> str:
    return f"""
        @SP
        AM=M-1
        D=M
        @{filename}.{current_function}${label}
        D; JNE
    """
