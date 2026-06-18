from collections import defaultdict
from dataclasses import dataclass

KIND_REGISTRY = {
    "var": "local",
    "field": "this",
    "static": "static",
    "argument": "argument",
}


@dataclass
class Symbol:
    name: str
    type: str
    kind: str
    index: int


class SymbolTable:
    def __init__(self) -> None:
        self.entries: dict[str, Symbol] = {}
        self.counts: dict[str, int] = defaultdict(int)

    def define(self, symbol_name: str, symbol_type: str, symbol_kind: str) -> None:
        self.entries[symbol_name] = Symbol(
            symbol_name,
            symbol_type,
            symbol_kind,
            self.counts[symbol_kind],
        )

        self.counts[symbol_kind] += 1

    def var_count(self, symbol_kind: str) -> int:
        return self.counts[symbol_kind]

    def kind_of(self, symbol_name: str) -> str:
        return self.entries[symbol_name].kind

    def type_of(self, symbol_name: str) -> str:
        return self.entries[symbol_name].type

    def index_of(self, symbol_name: str) -> int:
        return self.entries[symbol_name].index

    def contains(self, symbol_name: str) -> bool:
        return symbol_name in self.entries


if __name__ == "__main__":
    s = SymbolTable()

    s.define("a", "int", "field")
    s.define("b", "boolean", "field")
