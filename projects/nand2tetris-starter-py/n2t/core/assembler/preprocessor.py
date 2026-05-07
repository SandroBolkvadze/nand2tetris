from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Protocol

from n2t.core.assembler.constants import COMMENT, PREDEFINED_SYMBOLS, VAR_BASE_ADDRESS


class AssemblyPreprocessor(Protocol):
    def process(self, _assembly: Iterable[str]) -> Iterable[str]:
        pass


@dataclass
class AssemblyIdentity:
    def process(self, _assembly: Iterable[str]) -> Iterable[str]:
        return _assembly


@dataclass
class AssemblySanitizer:
    next: AssemblyPreprocessor = field(default_factory=AssemblyIdentity)

    def process(self, _assembly: Iterable[str]) -> Iterable[str]:
        processed = []

        for line in _assembly:
            if COMMENT in line:
                line = line[: line.find(COMMENT)]

            line = line.replace(" ", "")

            if len(line):
                processed.append(line)

        return self.next.process(processed)


@dataclass
class AssemblySymbolResolver:
    next: AssemblyPreprocessor = field(default_factory=AssemblyIdentity)

    def labels_for(self, _assembly: Iterable[str]) -> dict[str, int]:
        labels = {}
        address = 0

        for line in _assembly:
            if line.startswith("("):
                labels[line[1:-1]] = address
            else:
                address += 1

        return labels

    def process(self, _assembly: Iterable[str]) -> Iterable[str]:
        processed = []
        var_address = VAR_BASE_ADDRESS
        symbol_table = deepcopy(PREDEFINED_SYMBOLS) | self.labels_for(_assembly)

        for line in _assembly:
            symbol = line[1:]

            if line.startswith("("):
                continue

            if not line.startswith("@") or symbol.isdigit():
                processed.append(line)
                continue

            resolved = symbol_table.get(symbol)

            if resolved is None:
                symbol_table[symbol] = resolved = var_address
                var_address += 1

            processed.append(f"@{resolved}")

        return self.next.process(processed)
