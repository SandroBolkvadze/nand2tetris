from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class VmLabelTranslator:
    filename: str

    def translate(self, line: str) -> Iterable[str]:
        command, label = line.split()

        asm = f"""
            ({self.filename}.{label})
        """

        return asm.splitlines()
