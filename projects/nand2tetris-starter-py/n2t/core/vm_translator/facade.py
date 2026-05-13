from dataclasses import dataclass
from typing import Iterable

from n2t.core.vm_translator.arithmetic import VmArithmeticTranslator
from n2t.core.vm_translator.branch import VmBranchTranslator
from n2t.core.vm_translator.function import VmFunctionTranslator
from n2t.core.vm_translator.label import VmLabelTranslator
from n2t.core.vm_translator.pop import VmPopTranslator
from n2t.core.vm_translator.preprocessor import Preprocessor
from n2t.core.vm_translator.push import VmPushTranslator
from n2t.core.vm_translator.state import VmTranslatorState

_ARITHMETIC_COMMANDS = [
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

_PUSH_COMMANDS = [
    "push",
]

_POP_COMMANDS = [
    "pop",
]

_LABEL_COMMANDS = [
    "label",
]

_BRANCH_COMMANDS = [
    "goto",
    "if-goto",
]

_FUNCTION_COMMANDS = [
    "function",
    "return",
    "call",
]

@dataclass
class VmTranslator:
    filename: str

    @classmethod
    def create(cls, filename: str):
        return cls(filename)

    def translate(self, _vm_instructions: Iterable[str]) -> Iterable[str]:
        _vm_instructions_sanitized = Preprocessor().process(_vm_instructions)
        state = VmTranslatorState(filename=self.filename)

        asm = []

        for line in _vm_instructions_sanitized:
            tokens = line.split()

            if tokens[0] in _ARITHMETIC_COMMANDS:
                asm.extend(VmArithmeticTranslator(state).translate(line))
            elif tokens[0] in _PUSH_COMMANDS:
                asm.extend(VmPushTranslator(self.filename).translate(line))
            elif tokens[0] in _POP_COMMANDS:
                asm.extend(VmPopTranslator(self.filename).translate(line))
            elif tokens[0] in _LABEL_COMMANDS:
                asm.extend(VmLabelTranslator(self.filename).translate(line))
            elif tokens[0] in _BRANCH_COMMANDS:
                asm.extend(VmBranchTranslator(self.filename).translate(line))
            elif tokens[0] in _FUNCTION_COMMANDS:
                asm.extend(VmFunctionTranslator(state).translate(line))
            else:
                raise Exception(f"Unknown command <{tokens}>")

        return asm
