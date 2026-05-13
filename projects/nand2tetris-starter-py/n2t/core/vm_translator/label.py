from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

_LABEL_COMMANDS = [
    "label",
]


@dataclass
class VmLabelTranslator:
    filename: str

    def translate(self, line: str) -> Iterable[str]:
        command, label = line.split()

        asm = f"""
            ({self.filename}.{label})
        """

        return asm.splitlines()
