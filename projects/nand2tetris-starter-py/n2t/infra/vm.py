from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from n2t.core.vm_translator.bootstrap import VmBootstrapGenerator
from n2t.core.vm_translator.facade import VmTranslator as DefaultVmTranslator
from n2t.infra.io import File, FileFormat


@dataclass
class VmProgram:
    path: Path

    @classmethod
    def load_from(cls, _file_or_directory_name: str) -> VmProgram:
        return cls(Path(_file_or_directory_name))

    def translate(self) -> None:
        if self.path.is_dir():
            paths = [path for path in self.path.iterdir() if path.suffix == ".vm"]
        else:
            paths = [self.path]

        asm: list[str] = []

        if len(paths) > 1:
            asm.extend(VmBootstrapGenerator().generate())

        for path in paths:
            asm.extend(DefaultVmTranslator(path.stem).translate(File(path).load()))

        if self.path.is_dir():
            asm_file = File(FileFormat.asm.convert(self.path / self.path.stem))
        else:
            asm_file = File(FileFormat.asm.convert(self.path))

        asm_file.save(asm)
