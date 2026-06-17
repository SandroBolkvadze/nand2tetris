from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from n2t.core.compiler.analyzer import JackAnalyzer
from n2t.infra.io import File


@dataclass
class JackProgram:
    path: Path

    @classmethod
    def load_from(cls, _file_or_directory_name: str) -> JackProgram:
        return cls(Path(_file_or_directory_name))

    def compile(self) -> None:
        analyzer = JackAnalyzer(self.path)
        File(Path(self.path.parent / f"{self.path.stem}T").with_suffix(".xml")).save(analyzer.analyze())
