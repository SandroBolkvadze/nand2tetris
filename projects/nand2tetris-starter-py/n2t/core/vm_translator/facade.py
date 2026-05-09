from dataclasses import dataclass
from typing import Iterable

_PUSH_POP_COMMANDS = [
    "push", "pop",
]

_ARITHMETIC_LOGICAL_COMMANDS = [
    "add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not",
]


@dataclass
class VmTranslator:

    @classmethod
    def create(cls):
        return cls()

    def translate(self, _vm_code: Iterable[str]) -> Iterable[str]:
        asm = []

        for line in _vm_code:
            tokens = line.split()

            if tokens[0] in _ARITHMETIC_LOGICAL_COMMANDS:
                raise Exception("Not Implemented Yet")

            if tokens[0] in _PUSH_POP_COMMANDS:
                raise Exception("Not Implemented Yet")

        return asm
