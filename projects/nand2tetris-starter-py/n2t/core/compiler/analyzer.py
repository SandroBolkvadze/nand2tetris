from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from n2t.core.compiler.tokenizer import JackTokenizer


@dataclass
class JackAnalyzer:
    path: Path

    def analyze(self) -> Iterable[str]:
        tokenizer = JackTokenizer(str(self.path))

        xml = ["<tokens>\r"]
        while tokenizer.has_more_tokens():
            token, token_type = tokenizer.advance(), tokenizer.token_type()

            # check if token is < or >
            if token == "<":
                token = "&lt;"
            elif token == ">":
                token = "&gt;"

            xml.append(f"<{token_type}> {token} </{token_type}>\r")
        xml.append("</tokens>\r")

        return xml


