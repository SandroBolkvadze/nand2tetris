from collections.abc import Iterable
from dataclasses import dataclass

from n2t.core.vm_translator.function_commands.function import vm_call


@dataclass
class VmBootstrapGenerator:
    def generate(self) -> Iterable[str]:
        asm = ""

        asm += """
            // set SP = 256
            @256
            D=A
            @SP
            M=D
        """

        asm += vm_call("OS", "Sys.init", 0, 0)

        return [line.strip() for line in asm.splitlines() if len(line)]
