from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from n2t.core.vm_translator.push_pop_commands.push import push_constant, push_d
from n2t.core.vm_translator.utils.state import VmTranslatorState

FUNCTION_COMMANDS = [
    "function",
    "return",
    "call",
]


@dataclass
class VmFunctionTranslator:
    state: VmTranslatorState

    def translate(self, line: str) -> Iterable[str]:
        commands = line.split()

        asm = None
        match commands[0]:
            case "call":
                _, callee, n_args = commands[0], commands[1], int(commands[2])
                self.state.current_function_ret_count += 1
                asm = vm_call(
                    self.state.current_function,
                    callee,
                    n_args,
                    self.state.current_function_ret_count,
                )
            case "function":
                _, function_name, n_vars = commands[0], commands[1], int(commands[2])
                self.state.current_function = function_name
                asm = vm_function(function_name, n_vars)
            case "return":
                asm = vm_return()
            case _:
                raise Exception(f"Command <{line}> not found")

        return [token.strip() for token in asm.splitlines() if len(token)]


def vm_call(caller: str, callee: str, callee_nargs: int, caller_ret_count: int) -> str:
    ret_label = f"{caller}$ret.{caller_ret_count}"

    return f"""
        // push return address
        @{ret_label}
        D=A
        {push_d()}

        // push LCL
        @LCL
        D=M
        {push_d()}

        // push ARG
        @ARG
        D=M
        {push_d()}

        // push THIS
        @THIS
        D=M
        {push_d()}

        // push THAT
        @THAT
        D=M
        {push_d()}

        // set ARG = SP - 5 - nArgs
        @SP
        D=M
        @5
        D=D-A
        @{callee_nargs}
        D=D-A
        @ARG
        M=D

        // set LCL = SP
        @SP
        D=M
        @LCL
        M=D

        // goto function_name
        @{callee}
        0; JMP

        ({ret_label})
    """


def vm_function(function_name: str, n_vars: int) -> str:
    function = f"""
        ({function_name})
        // push local variables
    """

    function += push_constant(0) * n_vars

    return function


def vm_return() -> str:
    return """
        // save frame end
        @LCL
        D=M
        @R13
        M=D

        // save return address
        @LCL
        D=M
        @5
        D=D-A
        A=D
        D=M
        @R14
        M=D

        // replace arguments with caller pushed return value
        @SP
        AM=M-1
        D=M
        @ARG
        A=M
        M=D

        // recycle memory used by caller
        @ARG
        D=M
        @SP
        M=D+1

        // restore THAT
        @R13
        MD=M-1
        A=D
        D=M
        @THAT
        M=D

        // restore THIS
        @R13
        MD=M-1
        A=D
        D=M
        @THIS
        M=D

        // restore ARG
        @R13
        MD=M-1
        A=D
        D=M
        @ARG
        M=D

        // restore LCL
        @R13
        MD=M-1
        A=D
        D=M
        @LCL
        M=D

        // goto return address
        @R14
        A=M
        0; JMP
    """
