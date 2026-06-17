from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from n2t.core.compiler.tokenizer import JackTokenizer
from n2t.infra.io import File


@dataclass
class JackProgram:
    path: Path

    @classmethod
    def load_from(cls, _file_or_directory_name: str) -> JackProgram:
        return cls(Path(_file_or_directory_name))

    def compile(self) -> None:
        tokenizer = JackTokenizer(str(self.path))

        xml = ["<tokens>\r"]
        while tokenizer.has_more_tokens():
            token, token_type = tokenizer.advance(), tokenizer.token_type()
            xml.append(f"<{token_type}> {token} </{token_type}>\r")
        xml.append("</tokens>\r")

        File(Path(self.path.parent / f"{self.path.stem}T").with_suffix(".xml")).save(xml)
