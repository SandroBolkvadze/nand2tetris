from collections import defaultdict

KIND_REGISTRY = {
    "field": "this",
    "static": "static",
    "argument": "argument",
    "var": "local",
}


class SymbolTable:
    def __init__(self) -> None:
        self.entries: dict[str, dict[str, str | int]] = {}
        self.counts: dict[str, int] = defaultdict(int)

    def define(self, symbol_name: str, symbol_type: str, symbol_kind: str) -> None:
        self.entries[symbol_name] = {
            "name": symbol_name,
            "type": symbol_type,
            "kind": symbol_kind,
            "index": self.counts[symbol_kind],
        }

        self.counts[symbol_kind] += 1

    def var_count(self, symbol_kind: str) -> int:
        return self.counts[symbol_kind]

    def kind_of(self, symbol_name: str) -> str:
        return self.entries[symbol_name]["kind"]

    def type_of(self, symbol_name: str) -> str:
        return self.entries[symbol_name]["type"]

    def index_of(self, symbol_name: str) -> int:
        return self.entries[symbol_name]["index"]

    def contains(self, symbol_name) -> bool:
        return symbol_name in self.entries


if __name__ == "__main__":
    s = SymbolTable()

    s.define("a", "int", "field")
    s.define("b", "boolean", "field")
