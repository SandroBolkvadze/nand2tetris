from __future__ import annotations

from n2t.core.compiler.constants import (
    IDENTIFIER,
    INT_CONST,
    KEYWORD_CONST,
    OP,
    STRING_CONST,
    UNARY_OP,
)
from n2t.core.compiler.symbols import KIND_REGISTRY, SymbolTable
from n2t.core.compiler.tokenizer import JackTokenizer
from n2t.core.compiler.writer import VMWriter


class CompilationEngine:
    def __init__(self, tokenizer: JackTokenizer) -> None:
        self.tokenizer = tokenizer
        self.tokenizer.advance()

        self.branch_count = 0
        self.subroutine_type = self.subroutine_name = self.subroutine_return_type = ""

        self.class_symbol_table = SymbolTable()
        self.subroutine_symbol_table = SymbolTable()

        self.vm_writer = VMWriter()

        self.compile_class()

    def find_var_name(self, var_name: str) -> tuple[str, str, int] | None:
        if self.subroutine_symbol_table.contains(var_name):
            return (
                self.subroutine_symbol_table.type_of(var_name),
                self.subroutine_symbol_table.kind_of(var_name),
                self.subroutine_symbol_table.index_of(var_name),
            )
        if self.class_symbol_table.contains(var_name):
            return (
                self.class_symbol_table.type_of(var_name),
                self.class_symbol_table.kind_of(var_name),
                self.class_symbol_table.index_of(var_name),
            )
        return None

    def generate_label(self) -> str:
        label = f"{self.class_name}.label.{self.branch_count}"
        self.branch_count += 1
        return label

    def process_type(self) -> None:
        if self.tokenizer.token_type() == IDENTIFIER:
            self.process(self.tokenizer.identifier())
        else:
            self.process(["int", "char", "boolean"])

    def process(self, expected: list[str] | str = "") -> None:
        if isinstance(expected, str):
            expected = [expected]

        current = self.tokenizer.current_token()
        if current in expected:
            self.tokenizer.advance()
        else:
            raise Exception(f"Expected {expected}, Got {self.tokenizer.keyword()}")

    def compile_class(self) -> None:
        self.process("class")
        self.class_name = self.tokenizer.identifier()
        self.process(self.class_name)
        self.process("{")

        while True:
            match self.tokenizer.current_token():
                case "static" | "field":
                    self.compile_class_var_dec()
                case "constructor" | "function" | "method":
                    self.compile_subroutine_dec()
                case _:
                    break

        self.process("}")

    def compile_class_var_dec(self) -> None:
        # process class vars
        symbol_kind = self.tokenizer.current_token()
        self.process(["static", "field"])

        symbol_type = self.tokenizer.current_token()
        self.process_type()

        while self.tokenizer.current_token() != ";":
            symbol_name = self.tokenizer.current_token()
            self.process(symbol_name)

            self.class_symbol_table.define(
                symbol_name, symbol_type, KIND_REGISTRY[symbol_kind]
            )

            if self.tokenizer.current_token() == ",":
                self.process(",")

        self.process(";")

    def compile_subroutine_dec(self) -> None:
        self.subroutine_symbol_table = SymbolTable()

        self.subroutine_type = self.tokenizer.current_token()
        self.process(["constructor", "function", "method"])
        if self.tokenizer.current_token() == "void":
            self.subroutine_return_type = "void"
            self.process("void")
        else:
            self.subroutine_return_type = self.tokenizer.current_token()
            self.process_type()

        if self.subroutine_type == "method":
            self.subroutine_symbol_table.define("this", self.class_name, "argument")
            pass

        self.subroutine_name = self.tokenizer.identifier()
        self.process(self.subroutine_name)
        self.process("(")
        self.compile_parameter_list()
        self.process(")")

        self.compile_subroutine_body()

    def compile_parameter_list(self) -> None:
        if self.tokenizer.current_token() == ")":
            return

        # process subroutine arguments
        while self.tokenizer.current_token() != ")":
            symbol_type = self.tokenizer.current_token()
            self.process(symbol_type)

            symbol_name = self.tokenizer.current_token()
            self.process(symbol_name)

            self.subroutine_symbol_table.define(
                symbol_name, symbol_type, KIND_REGISTRY["argument"]
            )

            if self.tokenizer.current_token() == ",":
                self.process(",")

    def compile_subroutine_body(self) -> None:
        self.process("{")
        while self.tokenizer.current_token() == "var":
            self.compile_var_dec()

        n_vargs = self.subroutine_symbol_table.var_count(KIND_REGISTRY["var"])
        self.vm_writer.write_function(
            f"{self.class_name}.{self.subroutine_name}", n_vargs
        )

        if self.subroutine_type == "constructor":
            n_fields = self.class_symbol_table.var_count(KIND_REGISTRY["field"])
            self.vm_writer.write_push("constant", n_fields)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)

        elif self.subroutine_type == "method":
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)

        self.compile_statements()
        self.process("}")

    def compile_var_dec(self) -> None:
        symbol_kind = "var"
        self.process(symbol_kind)

        symbol_type = self.tokenizer.current_token()
        self.process_type()

        while self.tokenizer.current_token() != ";":
            symbol_name = self.tokenizer.current_token()
            self.process(symbol_name)

            self.subroutine_symbol_table.define(
                symbol_name, symbol_type, KIND_REGISTRY[symbol_kind]
            )

            if self.tokenizer.current_token() == ";":
                break

            self.process(",")

        self.process(";")

    def compile_statements(self) -> None:
        while self.tokenizer.current_token() != "}":
            match self.tokenizer.current_token():
                case "let":
                    self.compile_let()
                case "if":
                    self.compile_if()
                case "while":
                    self.compile_while()
                case "do":
                    self.compile_do()
                case "return":
                    self.compile_return()
                case _:
                    raise Exception(f"Bad token {self.tokenizer.current_token()}")

    def compile_let(self) -> None:
        self.process("let")

        var_name = self.tokenizer.identifier()
        self.process(var_name)
        result = self.find_var_name(var_name)

        if result is None:
            raise Exception(f"Variable {var_name} not defined")

        symbol_type, symbol_kind, symbol_index = result

        if self.tokenizer.current_token() == "[":
            self.vm_writer.write_push(symbol_kind, symbol_index)

            self.process("[")
            self.compile_expression()
            self.process("]")

            self.vm_writer.write_arithmetic("+")

            self.process("=")
            self.compile_expression()
            self.process(";")

            self.vm_writer.write_pop("temp", 0)
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)
        else:
            self.process("=")
            self.compile_expression()
            self.vm_writer.write_pop(symbol_kind, symbol_index)
            self.process(";")

    def compile_if(self) -> None:
        label1 = self.generate_label()
        label2 = self.generate_label()

        self.process("if")
        self.process("(")
        self.compile_expression()
        self.process(")")

        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if(label1)

        self.process("{")
        self.compile_statements()
        self.process("}")

        self.vm_writer.write_goto(label2)
        self.vm_writer.write_label(label1)

        if self.tokenizer.current_token() == "else":
            self.process("else")
            self.process("{")
            self.compile_statements()
            self.process("}")

        self.vm_writer.write_label(label2)

    def compile_while(self) -> None:
        label1 = self.generate_label()
        label2 = self.generate_label()

        self.vm_writer.write_label(label1)

        self.process("while")
        self.process("(")
        self.compile_expression()
        self.process(")")

        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if(label2)

        self.process("{")
        self.compile_statements()
        self.process("}")
        self.vm_writer.write_goto(label1)

        self.vm_writer.write_label(label2)

    def compile_do(self) -> None:
        self.process("do")
        self.compile_expression()
        self.vm_writer.write_pop("temp", 0)
        self.process(";")

    def compile_return(self) -> None:
        self.process("return")
        if self.tokenizer.current_token() != ";":
            self.compile_expression()
        else:
            self.vm_writer.write_push("constant", 0)

        self.vm_writer.write_return()
        self.process(";")

    def compile_expression(self) -> None:
        self.compile_term()

        while self.tokenizer.current_token() in OP:
            op = self.tokenizer.current_token()
            self.process(op)
            self.compile_term()
            self.vm_writer.write_arithmetic(op)

    def compile_term(self) -> None:
        current_token = self.tokenizer.current_token()

        if self.tokenizer.token_type() == INT_CONST:
            self.vm_writer.write_push("constant", int(current_token))
            self.process(current_token)
            return

        if self.tokenizer.token_type() == STRING_CONST:
            self.vm_writer.write_push("constant", len(current_token))
            self.vm_writer.write_call("String.new", 1)

            for ch in current_token:
                self.vm_writer.write_push("constant", ord(ch))
                self.vm_writer.write_call("String.appendChar", 2)

            self.process(current_token)
            return

        if current_token in KEYWORD_CONST:
            match current_token:
                case "true":
                    self.vm_writer.write_push("constant", 0).write_arithmetic("not")
                case "this":
                    self.vm_writer.write_push("pointer", 0)
                case "false" | "null":
                    self.vm_writer.write_push("constant", 0)

            self.process(current_token)
            return

        if current_token in UNARY_OP:
            self.process(current_token)
            self.compile_term()
            self.vm_writer.write_arithmetic("neg" if current_token == "-" else "not")
            return

        if current_token == "(":
            self.process("(")
            self.compile_expression()
            self.process(")")
            return

        prev_token = self.tokenizer.current_token()
        self.process(prev_token)

        match self.tokenizer.current_token():
            case "(":
                self.vm_writer.write_push("pointer", 0)
                self.process("(")
                nargs = self.compile_expression_list()
                self.process(")")
                self.vm_writer.write_call(f"{self.class_name}.{prev_token}", nargs + 1)
            case "[":
                result = self.find_var_name(prev_token)
                if result is None:
                    raise Exception(f"Variable {prev_token} not defined")

                symbol_type, symbol_kind, symbol_index = result

                self.vm_writer.write_push(symbol_kind, symbol_index)

                self.process("[")
                self.compile_expression()
                self.process("]")

                self.vm_writer.write_arithmetic("+")
                self.vm_writer.write_pop("pointer", 1)
                self.vm_writer.write_push("that", 0)

            case ".":
                self.process(".")
                subroutine_name = self.tokenizer.identifier()
                self.process(subroutine_name)
                self.process("(")

                result = self.find_var_name(prev_token)
                if result:
                    symbol_type, symbol_kind, symbol_index = result
                    self.vm_writer.write_push(symbol_kind, symbol_index)
                    nargs = self.compile_expression_list()
                    self.vm_writer.write_call(
                        f"{symbol_type}.{subroutine_name}", nargs + 1
                    )
                else:
                    nargs = self.compile_expression_list()
                    self.vm_writer.write_call(f"{prev_token}.{subroutine_name}", nargs)

                self.process(")")

            case _:
                result = self.find_var_name(prev_token)
                if result:
                    _, symbol_kind, symbol_index = result
                    self.vm_writer.write_push(symbol_kind, symbol_index)

    def compile_expression_list(self) -> int:
        if self.tokenizer.current_token() == ")":
            return 0

        num_expressions = 1
        self.compile_expression()

        while self.tokenizer.current_token() == ",":
            self.process(",")
            self.compile_expression()
            num_expressions += 1

        return num_expressions
