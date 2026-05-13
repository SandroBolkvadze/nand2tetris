from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from n2t.core.vm_translator.utils.state import VmTranslatorState

LABEL_COMMANDS = [
    "label",
]


@dataclass
class VmLabelTranslator:
    state: VmTranslatorState

    def translate(self, line: str) -> Iterable[str]:
        command, label = line.split()

        asm = f"({self.state.filename}.{self.state.current_function}${label})"

        return [line.strip() for line in asm.splitlines() if len(line)]
