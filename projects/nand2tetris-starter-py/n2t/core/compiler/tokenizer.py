from dataclasses import dataclass
from pathlib import Path

from n2t.core.compiler.constants import (
    IDENTIFIER,
    INT_CONST,
    KEYWORD,
    KEYWORDS,
    STRING_CONST,
    SYMBOL,
    SYMBOLS,
)
from n2t.infra.io import File


@dataclass
class JackTokenizer:
    def __init__(self, path: str) -> None:
        self.content = "".join(f"{line}\n" for line in File(Path(path)).load())
        self.token = self.is_str = None
        self.position = 0

    def _align(self) -> bool:
        old_position = self.position

        while self.position < len(self.content):
            if self.content[self.position] in [" ", "\n"]:
                self.position += 1
            elif self.content[self.position : self.position + 2] == "//":
                self.position = self.content.find("\n", self.position) + 1
            elif self.content[self.position : self.position + 2] in ["/*", "/**"]:
                self.position = self.content.find("*/", self.position) + 2
            else:
                break

        return old_position != self.position

    def has_more_tokens(self) -> bool:
        self._align()
        return self.position != len(self.content)

    def advance(self) -> str:
        self._align()

        if not self.has_more_tokens():
            return ""

        # print("position:", self.position)
        start = self.position
        self.position += 1
        token = self.content[start]

        # check if token is string
        if token == '"':
            self.position = self.content.find('"', self.position + 1) + 1
            self.token = self.content[start + 1 : self.position - 1]
            self.is_str = True
            return self.token

        # advance one character on each cycle
        while True:
            if self._align() or self.position == len(self.content):
                break
            ch = self.content[self.position]
            if ch == " " or ch in SYMBOLS or token in SYMBOLS:
                break
            token += ch
            self.position += 1

        # save token
        self.token = token
        self.is_str = False

        return token

    def token_type(self) -> str:
        if self.token in KEYWORDS:
            return KEYWORD
        if self.token in SYMBOLS:
            return SYMBOL
        if self.token.isdigit():
            return INT_CONST
        if self.is_str:
            return STRING_CONST
        return IDENTIFIER

    def current_token(self) -> str:
        return self.token

    def keyword(self) -> str:
        assert self.token_type() == KEYWORD, (
            f"Expected {KEYWORD}, Got {self.token_type()}"
        )
        return self.token

    def symbol(self) -> str:
        assert self.token_type() == SYMBOL, (
            f"Expected {SYMBOL}, Got {self.token_type()}"
        )
        return self.token

    def identifier(self) -> str:
        assert self.token_type() == IDENTIFIER, (
            f"Expected {IDENTIFIER}, Got {self.token_type()}"
        )
        return self.token

    def int_val(self) -> str:
        assert self.token_type() == INT_CONST, (
            f"Expected {INT_CONST}, Got {self.token_type()}"
        )
        return self.token

    def string_val(self) -> str:
        assert self.token_type() == STRING_CONST, (
            f"Expected {STRING_CONST}, Got {self.token_type()}"
        )
        return self.token
