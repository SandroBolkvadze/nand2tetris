from collections.abc import Iterable
from dataclasses import dataclass
from typing import Self

from n2t.core.vm_translator.arithmetic import (
    _ARITHMETIC_COMMANDS,
    VmArithmeticTranslator,
)
from n2t.core.vm_translator.branch import _BRANCH_COMMANDS, VmBranchTranslator
from n2t.core.vm_translator.clean import Preprocessor
from n2t.core.vm_translator.function import _FUNCTION_COMMANDS, VmFunctionTranslator
from n2t.core.vm_translator.label import _LABEL_COMMANDS, VmLabelTranslator
from n2t.core.vm_translator.pop import _POP_COMMANDS, VmPopTranslator
from n2t.core.vm_translator.push import _PUSH_COMMANDS, VmPushTranslator
from n2t.core.vm_translator.state import VmTranslatorState


@dataclass
class VmTranslator:
    filename: str

    @classmethod
    def create(cls, filename: str) -> Self:
        return cls(filename)

    def translate(self, _vm_instructions: Iterable[str]) -> Iterable[str]:
        _vm_instructions_sanitized = Preprocessor().process(_vm_instructions)
        state = VmTranslatorState(filename=self.filename)

        asm: list[str] = []

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
