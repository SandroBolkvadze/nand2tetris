from __future__ import annotations

from typing import Callable, Tuple

from n2t.core.compiler.symbols import SymbolTable, KIND_REGISTRY
from n2t.core.compiler.tokenizer import JackTokenizer, IDENTIFIER, INT_CONST, STRING_CONST
from n2t.core.compiler.writer import VMWriter

OP            = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
UNARY_OP      = ["-", "~"]
KEYWORD_CONST = ["true", "false", "null", "this"]

class CompilationEngineV1:
    def __init__(self, tokenizer: JackTokenizer) -> None:
        self.xml = []
        self.tokenizer = tokenizer
        self.tokenizer.advance()

        self.branch_count = 0
        self.subroutine_type = None
        self.subroutine_return_type = None
        self.subroutine_name = None

        # init symbol tables
        self.class_symbol_table = SymbolTable()
        self.subroutine_symbol_table = SymbolTable()

        # init vm_writer
        self.vm_writer = VMWriter()

        # start class compilation
        self.compile_class()


    def print_xml_token(self, token: str, prefix="") -> None:
        token_type = self.tokenizer.token_type()

        if token == "<":
            token = "&lt;"
        elif token == ">":
            token = "&gt;"
        elif token == "&":
            token = "&amp;"
        elif token == "\"":
            token = "&quot;"

        self.xml.append(f"{prefix}<{token_type}> {token} </{token_type}>\r")

    def find_var_name(self, var_name: str) -> tuple[str, str, int] | None:
        if self.subroutine_symbol_table.contains(var_name):
            return self.subroutine_symbol_table.type_of(var_name), self.subroutine_symbol_table.kind_of(var_name), self.subroutine_symbol_table.index_of(var_name)
        elif self.class_symbol_table.contains(var_name):
            return self.class_symbol_table.type_of(var_name), self.class_symbol_table.kind_of(var_name), self.class_symbol_table.index_of(var_name)

        return None

    def process_type(self, prefix=""):
        if self.tokenizer.token_type() == IDENTIFIER:
            self.process(self.tokenizer.identifier(), prefix)
        else:
            self.process(["int", "char", "boolean"], prefix)

    def process_list(self, get_token: Callable[[], str], prefix=""):
        self.process(get_token(), prefix)

        while self.tokenizer.current_token() == ",":
            self.process(",", prefix)
            self.process(get_token(), prefix)

    def process(self, expected: list[str] | str, prefix="") -> None:
        # for convenience
        if isinstance(expected, str):
            expected = [expected]

        current = self.tokenizer.current_token()
        if current in expected:
            self.print_xml_token(current, prefix)
            self.tokenizer.advance()
        else:
            raise Exception(f"Expected {expected}, Got {self.tokenizer.keyword()}")


    def compile_class(self, prefix="") -> None:
        self.xml.append(f"{prefix}<class>\r")

        next_prefix = prefix + "  "

        self.process("class", next_prefix)
        self.class_name = self.tokenizer.identifier()
        self.process(self.class_name, next_prefix)
        self.process("{", next_prefix)

        while True:
            match self.tokenizer.current_token():
                case "static" | "field":
                    self.compile_class_var_dec(next_prefix)
                case "constructor" | "function" | "method":
                    self.compile_subroutine_dec(next_prefix)
                case _:
                    break

        self.process("}", next_prefix)
        self.xml.append(f"{prefix}</class>\r")



    def compile_class_var_dec(self, prefix="") -> None:
        self.xml.append(f"{prefix}<classVarDec>\r")

        next_prefix = prefix + "  "

        # process class vars
        symbol_kind = self.tokenizer.current_token()
        self.process(["static", "field"], next_prefix)

        symbol_type = self.tokenizer.current_token()
        self.process_type(next_prefix)

        while self.tokenizer.current_token() != ";":
            symbol_name = self.tokenizer.current_token()
            self.process(symbol_name, next_prefix)

            self.class_symbol_table.define(symbol_name, symbol_type, KIND_REGISTRY[symbol_kind])

            if self.tokenizer.current_token() == ",":
                self.process(",", next_prefix)

        self.process(";", next_prefix)
        self.xml.append(f"{prefix}</classVarDec>\r")



    def compile_subroutine_dec(self, prefix="") -> None:
        self.subroutine_symbol_table = SymbolTable()

        self.xml.append(f"{prefix}<subroutineDec>\r")

        next_prefix = prefix + "  "

        self.subroutine_type = self.tokenizer.current_token()
        self.process(["constructor", "function", "method"], next_prefix)
        if self.tokenizer.current_token() == "void":
            self.subroutine_return_type = "void"
            self.process("void", next_prefix)
        else:
            self.subroutine_return_type = self.tokenizer.current_token()
            self.process_type(next_prefix)

        if self.subroutine_type == "method":
            self.subroutine_symbol_table.define("this", self.class_name, "argument")
            pass

        self.subroutine_name = self.tokenizer.identifier()
        self.process(self.subroutine_name, next_prefix)
        self.process("(", next_prefix)
        self.compile_parameter_list(next_prefix)
        self.process(")", next_prefix)

        self.compile_subroutine_body(next_prefix)

        self.xml.append(f"{prefix}</subroutineDec>\r")


    def compile_parameter_list(self, prefix="") -> None:
        self.xml.append(f"{prefix}<parameterList>\r")

        if self.tokenizer.current_token() == ")":
            self.xml.append(f"{prefix}</parameterList>\r")
            return

        next_prefix = prefix + "  "

        # process subroutine arguments
        while self.tokenizer.current_token() != ")":
            symbol_type = self.tokenizer.current_token()
            self.process(symbol_type, next_prefix)

            symbol_name = self.tokenizer.current_token()
            self.process(symbol_name, next_prefix)

            self.subroutine_symbol_table.define(symbol_name, symbol_type, KIND_REGISTRY["argument"])

            if self.tokenizer.current_token() == ",":
                self.process(",", next_prefix)

        self.xml.append(f"{prefix}</parameterList>\r")



    def compile_subroutine_body(self, prefix="") -> None:
        self.xml.append(f"{prefix}<subroutineBody>\r")

        next_prefix = prefix + "  "
        self.process("{", next_prefix)
        while self.tokenizer.current_token() == "var":
            self.compile_var_dec(next_prefix)

        nvargs = self.subroutine_symbol_table.var_count(KIND_REGISTRY["var"])
        self.vm_writer.write_function(f"{self.class_name}.{self.subroutine_name}", nvargs)

        if self.subroutine_type == "constructor":
            nfields = self.class_symbol_table.var_count(KIND_REGISTRY["field"])
            self.vm_writer.write_push("constant", nfields)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)

        elif self.subroutine_type == "method":
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)

        self.compile_statements(next_prefix)
        self.process("}", next_prefix)

        self.xml.append(f"{prefix}</subroutineBody>\r")


    def compile_var_dec(self, prefix="") -> None:
        self.xml.append(f"{prefix}<varDec>\r")
        next_prefix = prefix + "  "

        symbol_kind = "var"
        self.process(symbol_kind, next_prefix)

        symbol_type = self.tokenizer.current_token()
        self.process_type(next_prefix)

        while self.tokenizer.current_token() != ";":
            symbol_name = self.tokenizer.current_token()
            self.process(symbol_name, next_prefix)

            self.subroutine_symbol_table.define(symbol_name, symbol_type, KIND_REGISTRY[symbol_kind])

            if self.tokenizer.current_token() == ";":
                break

            self.process(",", next_prefix)

        self.process(";", next_prefix)
        self.xml.append(f"{prefix}</varDec>\r")


    def compile_statements(self, prefix="") -> None:
        self.xml.append(f"{prefix}<statements>\r")

        next_prefix = prefix + "  "
        while self.tokenizer.current_token() != "}":
            match self.tokenizer.current_token():
                case "let":
                    self.compile_let(next_prefix)
                case "if":
                    self.compile_if(next_prefix)
                case "while":
                    self.compile_while(next_prefix)
                case "do":
                    self.compile_do(next_prefix)
                case "return":
                    self.compile_return(next_prefix)
                case _:
                    raise Exception(f"Unexpected token in statements: {self.tokenizer.current_token()}")

        self.xml.append(f"{prefix}</statements>\r")

    def compile_let(self, prefix="") -> None:
        self.xml.append(f"{prefix}<letStatement>\r")

        next_prefix = prefix + "  "
        self.process("let", next_prefix)

        var_name = self.tokenizer.identifier()
        self.process(var_name, next_prefix)
        symbol_type, symbol_kind, symbol_index = self.find_var_name(var_name)

        if self.tokenizer.current_token() == "[":
            self.vm_writer.write_push(symbol_kind, symbol_index)

            self.process("[", next_prefix)
            self.compile_expression(next_prefix)
            self.process("]", next_prefix)

            self.vm_writer.write_arithmetic("+")

            self.process("=", next_prefix)
            self.compile_expression(next_prefix)
            self.process(";", next_prefix)

            self.vm_writer.write_pop("temp", 0)
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)
        else:
            self.process("=", next_prefix)
            self.compile_expression(next_prefix)
            self.vm_writer.write_pop(symbol_kind, symbol_index)
            self.process(";", next_prefix)

        self.xml.append(f"{prefix}</letStatement>\r")



    def compile_if(self, prefix="") -> None:
        self.xml.append(f"{prefix}<ifStatement>\r")
        next_prefix = prefix + "  "

        label1 = f"{self.class_name}.label.{self.branch_count}"
        self.branch_count += 1
        label2 = f"{self.class_name}.label.{self.branch_count}"
        self.branch_count += 1

        self.process("if", next_prefix)
        self.process("(", next_prefix)
        self.compile_expression(next_prefix)
        self.process(")", next_prefix)

        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if(label1)

        self.process("{", next_prefix)
        self.compile_statements(next_prefix)
        self.process("}", next_prefix)

        self.vm_writer.write_goto(label2)
        self.vm_writer.write_label(label1)

        if self.tokenizer.current_token() == "else":
            self.process("else", next_prefix)
            self.process("{", next_prefix)
            self.compile_statements(next_prefix)
            self.process("}", next_prefix)

        self.vm_writer.write_label(label2)
        self.xml.append(f"{prefix}</ifStatement>\r")

    def compile_while(self, prefix="") -> None:
        self.xml.append(f"{prefix}<whileStatement>\r")
        next_prefix = prefix + "  "

        label1 = f"{self.class_name}.label.{self.branch_count}"
        self.branch_count += 1
        label2 = f"{self.class_name}.label.{self.branch_count}"
        self.branch_count += 1


        self.vm_writer.write_label(label1)

        self.process("while", next_prefix)
        self.process("(", next_prefix)
        self.compile_expression(next_prefix)
        self.process(")", next_prefix)

        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if(label2)

        self.process("{", next_prefix)
        self.compile_statements(next_prefix)
        self.process("}", next_prefix)
        self.vm_writer.write_goto(label1)

        self.vm_writer.write_label(label2)
        self.xml.append(f"{prefix}</whileStatement>\r")

    def compile_do(self, prefix="") -> None:
        self.xml.append(f"{prefix}<doStatement>\r")
        next_prefix = prefix + "  "
        self.process("do", next_prefix)

        self.compile_expression(next_prefix)

        self.vm_writer.write_pop("temp", 0)

        self.process(";", next_prefix)
        self.xml.append(f"{prefix}</doStatement>\r")

    def compile_return(self, prefix="") -> None:
        self.xml.append(f"{prefix}<returnStatement>\r")
        next_prefix = prefix + "  "
        self.process("return", next_prefix)
        if self.tokenizer.current_token() != ";":
            self.compile_expression(next_prefix)
        else:
            self.vm_writer.write_push("constant", 0)

        self.vm_writer.write_return()

        self.process(";", next_prefix)
        self.xml.append(f"{prefix}</returnStatement>\r")



    def compile_expression(self, prefix="") -> None:
        self.xml.append(f"{prefix}<expression>\r")

        next_prefix = prefix + "  "
        self.compile_term(next_prefix)

        while self.tokenizer.current_token() in OP:
            op = self.tokenizer.current_token()
            self.process(op, next_prefix)
            self.compile_term(next_prefix)
            self.vm_writer.write_arithmetic(op)

        self.xml.append(f"{prefix}</expression>\r")


    def compile_term(self, prefix="") -> None:
        self.xml.append(f"{prefix}<term>\r")

        next_prefix = prefix + "  "

        current_token = self.tokenizer.current_token()

        if self.tokenizer.token_type() == INT_CONST:
            self.vm_writer.write_push("constant", int(current_token))
            self.process(current_token, next_prefix)
            self.xml.append(f"{prefix}</term>\r")
            return

        if self.tokenizer.token_type() == STRING_CONST:
            self.vm_writer.write_push("constant", len(current_token))
            self.vm_writer.write_call("String.new", 1)

            for ch in current_token:
                self.vm_writer.write_push("constant", ord(ch))
                self.vm_writer.write_call("String.appendChar", 2)

            self.process(current_token, next_prefix)
            self.xml.append(f"{prefix}</term>\r")
            return

        if current_token in KEYWORD_CONST:
            match current_token:
                case "false" | "null":
                    self.vm_writer.write_push("constant", 0)
                case "true":
                    self.vm_writer.write_push("constant", 0).write_arithmetic("not")
                case "this":
                    self.vm_writer.write_push("pointer", 0)
            self.process(current_token, next_prefix)
            self.xml.append(f"{prefix}</term>\r")
            return

        if current_token in UNARY_OP:
            self.process(current_token, next_prefix)
            self.compile_term(next_prefix)
            self.vm_writer.write_arithmetic("neg" if current_token == "-" else "not")
            self.xml.append(f"{prefix}</term>\r")
            return

        if current_token == "(":
            self.process("(", next_prefix)
            self.compile_expression(next_prefix)
            self.process(")", next_prefix)
            self.xml.append(f"{prefix}</term>\r")
            return

        prev_token = self.tokenizer.current_token()
        self.process(prev_token, next_prefix)

        match self.tokenizer.current_token():
            case "(":
                self.vm_writer.write_push("pointer", 0)
                self.process("(", next_prefix)
                nargs = self.compile_expression_list(next_prefix)
                self.process(")", next_prefix)
                self.vm_writer.write_call(f"{self.class_name}.{prev_token}", nargs + 1)
            case "[":
                result = self.find_var_name(prev_token)
                if not result:
                    raise Exception(f"{prev_token} variable should be defined")

                symbol_type, symbol_kind, symbol_index = self.find_var_name(prev_token)

                self.vm_writer.write_push(symbol_kind, symbol_index)

                self.process("[", next_prefix)
                self.compile_expression(next_prefix)
                self.process("]", next_prefix)

                self.vm_writer.write_arithmetic("+")
                self.vm_writer.write_pop("pointer", 1)
                self.vm_writer.write_push("that", 0)

            case ".":
                self.process(".", next_prefix)
                subroutine_name = self.tokenizer.identifier()
                self.process(subroutine_name, next_prefix)
                self.process("(", next_prefix)

                result = self.find_var_name(prev_token)
                if result:
                    symbol_type, symbol_kind, symbol_index = result
                    self.vm_writer.write_push(symbol_kind, symbol_index)
                    nargs = self.compile_expression_list(next_prefix)
                    self.vm_writer.write_call(f"{symbol_type}.{subroutine_name}", nargs + 1)
                else:
                    nargs = self.compile_expression_list(next_prefix)
                    self.vm_writer.write_call(f"{prev_token}.{subroutine_name}", nargs)

                self.process(")", next_prefix)

            case _:
                result = self.find_var_name(prev_token)
                if result:
                    _, symbol_kind, symbol_index = result
                    self.vm_writer.write_push(symbol_kind, symbol_index)

        self.xml.append(f"{prefix}</term>\r")


    def compile_expression_list(self, prefix="") -> int:
        self.xml.append(f"{prefix}<expressionList>\r")

        if self.tokenizer.current_token() == ")":
            self.xml.append(f"{prefix}</expressionList>\r")
            return 0

        num_expressions = 1
        next_prefix = prefix + "  "
        self.compile_expression(next_prefix)

        while self.tokenizer.current_token() == ",":
            self.process(",", next_prefix)
            self.compile_expression(next_prefix)
            num_expressions += 1

        self.xml.append(f"{prefix}</expressionList>\r")
        return num_expressions


if __name__ == "__main__":
    tokenizer = JackTokenizer("/home/sandro/code/nand2tetris/nand2tetris/projects/nand2tetris-starter-py/Test.jack")
    analyzer = CompilationEngineV1(tokenizer)

    print(analyzer.class_symbol_table.entries)
    print(analyzer.subroutine_symbol_table.entries)

    print("\n".join(analyzer.vm_writer.vm))
    # print("\n".join(analyzer.xml))

