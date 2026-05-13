from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Protocol

_COMMENT = "//"

@dataclass
class Preprocessor:

    def process(self, _vm_instructions: Iterable[str]) -> Iterable[str]:
        sanitized = []

        for line in _vm_instructions:
            comment_index = line.find(_COMMENT)

            if comment_index != -1:
                line = line[:comment_index]
            line = line.strip()

            if len(line) != 0:
                sanitized.append(line)

        return sanitized
