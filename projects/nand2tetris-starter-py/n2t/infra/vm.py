from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Protocol

from n2t.core.vm_translator.function import vm_call
from n2t.infra.io import File, FileFormat
from n2t.core.vm_translator.facade import VmTranslator as DefaultVmTranslator


@dataclass
class VmProgram:  # TODO: your work for Projects 7 and 8 starts here
    path: Path

    @classmethod
    def load_from(cls, _file_or_directory_name: str) -> VmProgram:
        return cls(Path(_file_or_directory_name))

    def translate(self) -> None:
        if self.path.is_dir():
            paths = [path for path in self.path.iterdir() if path.suffix == ".vm"]
        else:
            paths = [self.path]

        asm = []

        if len(paths) > 1:
            asm.extend(["@256", "D=A", "@SP", "M=D"])
            asm.extend(vm_call("OS", "Sys.init", 0, 0).splitlines())

        for path in paths:
            asm.extend(DefaultVmTranslator(path.stem).translate(File(path).load()))

        if self.path.is_dir():
            asm_file = File(FileFormat.asm.convert(self.path / self.path.stem))
        else:
            asm_file = File(FileFormat.asm.convert(self.path))

        asm_file.save(asm)
