from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from n2t.core.compiler.engine import CompilationEngine
from n2t.core.compiler.tokenizer import JackTokenizer


@dataclass
class JackAnalyzerV0:
    path: Path

    def analyze(self) -> Iterable[str]:
        tokenizer = JackTokenizer(str(self.path))

        xml = ["<tokens>\r"]
        while tokenizer.has_more_tokens():
            token, token_type = tokenizer.advance(), tokenizer.token_type()

            # check if token is "<" or ">"
            if token == "<":
                token = "&lt;"
            elif token == ">":
                token = "&gt;"
            elif token == "&":
                token = "&amp;"
            elif token == "\"":
                token = "&quot;"

            xml.append(f"<{token_type}> {token} </{token_type}>\r")
        xml.append("</tokens>\r")

        return xml


@dataclass
class JackAnalyzerV1:
    path: Path

    def analyze(self) -> Iterable[str]:
        engine = CompilationEngine(JackTokenizer(str(self.path)))
        return engine.xml

