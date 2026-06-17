from collections.abc import Iterable
from dataclasses import dataclass
from typing import Self

from n2t.core.vm_translator.arithmetic_commands.arithmetic import (
    ARITHMETIC_COMMANDS,
    VmArithmeticTranslator,
)
from n2t.core.vm_translator.branching_commands.branch import (
    BRANCH_COMMANDS,
    VmBranchTranslator,
)
from n2t.core.vm_translator.branching_commands.label import (
    LABEL_COMMANDS,
    VmLabelTranslator,
)
from n2t.core.vm_translator.function_commands.function import (
    FUNCTION_COMMANDS,
    VmFunctionTranslator,
)
from n2t.core.vm_translator.push_pop_commands.pop import POP_COMMANDS, VmPopTranslator
from n2t.core.vm_translator.push_pop_commands.push import (
    PUSH_COMMANDS,
    VmPushTranslator,
)
from n2t.core.vm_translator.utils.clean import Preprocessor
from n2t.core.vm_translator.utils.state import VmTranslatorState


@dataclass
class VmTranslator:
    filename: str

    @classmethod
    def create(cls, filename: str) -> Self:
        return cls(filename)

    def translate(self, _vm_instructions: Iterable[str]) -> Iterable[str]:
        _vm_instructions_preprocessed = Preprocessor().process(_vm_instructions)
        state = VmTranslatorState(filename=self.filename)
        asm: list[str] = []

        for line in _vm_instructions_preprocessed:
            tokens = line.split()

            if tokens[0] in ARITHMETIC_COMMANDS:
                asm.extend(VmArithmeticTranslator(state).translate(line))
            elif tokens[0] in PUSH_COMMANDS:
                asm.extend(VmPushTranslator(self.filename).translate(line))
            elif tokens[0] in POP_COMMANDS:
                asm.extend(VmPopTranslator(self.filename).translate(line))
            elif tokens[0] in LABEL_COMMANDS:
                asm.extend(VmLabelTranslator(state).translate(line))
            elif tokens[0] in BRANCH_COMMANDS:
                asm.extend(VmBranchTranslator(state).translate(line))
            elif tokens[0] in FUNCTION_COMMANDS:
                asm.extend(VmFunctionTranslator(state).translate(line))
            else:
                raise Exception(f"Unknown command <{tokens}>")

        return [line for line in asm if len(line)]
