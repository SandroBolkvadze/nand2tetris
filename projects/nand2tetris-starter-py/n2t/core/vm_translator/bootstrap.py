from collections.abc import Iterable
from dataclasses import dataclass

from n2t.core.vm_translator.function import vm_call


@dataclass
class VmBootstrapGenerator:
    def generate(self) -> Iterable[str]:
        asm = []

        asm.extend(
            """
            @256
            D=A
            @SP
            M=D
        """.splitlines()
        )

        asm.extend(vm_call("OS", "Sys.init", 0, 0).splitlines())

        return asm
