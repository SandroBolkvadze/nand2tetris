from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Protocol
from n2t.infra.io import File, FileFormat
from n2t.core.vm_translator.facade import VmTranslator as DefaultVmTranslator

@dataclass
class VmProgram:  # TODO: your work for Projects 7 and 8 starts here
    path: Path

    @classmethod
    def load_from(cls, _file_or_directory_name: str) -> VmProgram:
        return cls(Path(_file_or_directory_name))

    def translate(self) -> None:
        filename = self.path.stem
        print("filename:", filename)

        asm_file = File(FileFormat.asm.convert(self.path))
        asm_file.save(DefaultVmTranslator(filename).translate(self))
        # asm_file.save(self.translator.translate(self))

    def __iter__(self) -> Iterator[str]:
        yield from File(self.path).load()

class VmTranslator(Protocol):
    def translate(self, _vm_code: Iterable[str]) -> Iterable[str]:
        pass
