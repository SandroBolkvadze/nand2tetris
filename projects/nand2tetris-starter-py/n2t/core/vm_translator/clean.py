from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

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
