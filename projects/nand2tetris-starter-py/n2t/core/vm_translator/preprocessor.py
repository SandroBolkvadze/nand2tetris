from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Protocol

_COMMENT = "//"


class TranslatorChain(Protocol):
    def process(self, _vm_instructions: Iterable[str]) -> Iterable[str]:
        pass


@dataclass
class Identity:
    next: TranslatorChain = field(default=None)

    def process(self, _vm_instructions: Iterable[str]) -> Iterable[str]:
        return _vm_instructions


@dataclass
class Preprocessor:
    next: TranslatorChain = field(default_factory=Identity)

    def process(self, _vm_instructions: Iterable[str]) -> Iterable[str]:
        sanitized = []

        for line in _vm_instructions:
            comment_index = line.find(_COMMENT)

            if comment_index != -1:
                line = line[:comment_index]
            line = line.strip()

            if len(line) != 0:
                sanitized.append(line)

        return self.next.process(sanitized)
