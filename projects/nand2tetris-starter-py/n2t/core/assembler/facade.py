from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from n2t.core.assembler.preprocessor import (
    AssemblyPreprocessor,
    AssemblySanitizer,
    AssemblySymbolResolver,
)
from n2t.core.assembler.translator import (
    BasicAInstructionTranslator,
    BasicCInstructionTranslator,
    Translator,
)


@dataclass
class Assembler:
    preprocessor: AssemblyPreprocessor = field(
        default_factory=lambda: AssemblySanitizer(AssemblySymbolResolver())
    )
    a_translator: Translator = field(default_factory=BasicAInstructionTranslator)
    c_translator: Translator = field(default_factory=BasicCInstructionTranslator)

    @classmethod
    def create(cls) -> Assembler:
        return cls()

    def assemble(self, _assembly: Iterable[str]) -> Iterable[str]:
        preprocessed = self.preprocessor.process(_assembly)

        binary = []

        for line in preprocessed:
            if line.startswith("@"):
                binary.append(self.a_translator.binary_for(line))
            else:
                binary.append(self.c_translator.binary_for(line))

        return binary
