from typing import Self


class VMWriter:

    def __init__(self):
        self.vm = []

    def write_push(self, segment: str, index: int) -> Self:
        self.vm.append(f"push {segment} {index}")
        return self

    def write_pop(self, segment: str, index: int) -> Self:
        self.vm.append(f"pop {segment} {index}")
        return self

    def write_arithmetic(self, command: str) -> Self:
        vm_code = ""
        match command:
            case "+":
                vm_code = "add"
            case "-":
                vm_code = "sub"
            case "*":
                vm_code = "call Math.multiply 2"
            case "/":
                vm_code = "call Math.divide 2"
            case "&":
                vm_code = "and"
            case "|":
                vm_code = "or"
            case ">":
                vm_code = "gt"
            case "<":
                vm_code = "lt"
            case "=":
                vm_code = "eq"
            case "not":
                vm_code = "not"
            case "neg":
                vm_code = "neg"

        self.vm.append(vm_code)
        return self

    def write_label(self, label: str) -> Self:
        self.vm.append(f"label {label}")
        return self

    def write_goto(self, label: str) -> Self:
        self.vm.append(f"goto {label}")
        return self

    def write_if(self, label: str) -> Self:
        self.vm.append(f"if-goto {label}")
        return self

    def write_call(self, name: str, nargs: int) -> Self:
        self.vm.append(f"call {name} {nargs}")
        return self

    def write_function(self, name: str, nvars: int) -> Self:
        self.vm.append(f"function {name} {nvars}")
        return self

    def write_return(self) -> Self:
        self.vm.append(f"return")
        return self

    def write_custom(self, vm_code: str) -> Self:
        self.vm.append(vm_code)
        return self




