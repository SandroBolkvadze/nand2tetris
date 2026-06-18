from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from n2t.infra.io import File


@dataclass
class JackProgram:
    path: Path

    @classmethod
    def load_from(cls, _file_or_directory_name: str) -> JackProgram:
        return cls(Path(_file_or_directory_name))

    def compile(self) -> None:
        from n2t.core.compiler.analyzer import JackAnalyzerV0, JackAnalyzerV1
        from n2t.core.compiler.compiler import JackCompiler

        if self.path.is_dir():
            paths = [path for path in self.path.iterdir() if path.suffix == ".jack"]
        else:
            paths = [self.path]

        for path in paths:
            analyzer_v0 = JackAnalyzerV0(path)
            File(Path(path.parent / f"{path.stem}T").with_suffix(".xml")).save(
                analyzer_v0.analyze()
            )

            analyzer_v1 = JackAnalyzerV1(path)
            File(Path(path.parent / f"{path.stem}").with_suffix(".xml")).save(
                analyzer_v1.analyze()
            )

            compiler = JackCompiler(path)
            File(Path(path.parent / f"{path.stem}").with_suffix(".vm")).save(
                compiler.compile()
            )


# if __name__ == "__main__":
#     path = "/home/sandro/code/nand2tetris/nand2tetris/projects/nand2tetris-starter-py/tests/e2e/nand2tetris/projects/11"
#     for dir in Path(path).iterdir():
#         program = JackProgram(dir)
#         program.compile()
