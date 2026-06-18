from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from n2t.core.compiler.engine import CompilationEngine
from n2t.core.compiler.tokenizer import JackTokenizer

@dataclass
class JackCompiler:
    path: Path

    def compile(self) -> Iterable[str]:
        engine = CompilationEngine(JackTokenizer(str(self.path)))
        return engine.vm_writer.vm
