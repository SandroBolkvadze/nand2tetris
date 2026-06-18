from __future__ import annotations

from collections.abc import Callable

from n2t.core.compiler.engine import KEYWORD_CONST, OP, UNARY_OP
from n2t.core.compiler.tokenizer import (
    IDENTIFIER,
    INT_CONST,
    STRING_CONST,
    JackTokenizer,
)


class CompilationXMLEngine:
    def __init__(self, tokenizer: JackTokenizer) -> None:
        self.xml = []
        self.tokenizer = tokenizer
        self.tokenizer.advance()
        self.compile_class()

    def print_xml_token(self, token: str, prefix="") -> None:
        token_type = self.tokenizer.token_type()

        if token == "<":
            token = "&lt;"
        elif token == ">":
            token = "&gt;"
        elif token == "&":
            token = "&amp;"
        elif token == '"':
            token = "&quot;"

        self.xml.append(f"{prefix}<{token_type}> {token} </{token_type}>\r")

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
        self.process(self.tokenizer.identifier(), next_prefix)
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

        self.process(["static", "field"], next_prefix)
        self.process_type(next_prefix)
        self.process_list(self.tokenizer.identifier, next_prefix)
        self.process(";", next_prefix)
        self.xml.append(f"{prefix}</classVarDec>\r")

    def compile_subroutine_dec(self, prefix="") -> None:
        self.xml.append(f"{prefix}<subroutineDec>\r")

        next_prefix = prefix + "  "
        self.process(["constructor", "function", "method"], next_prefix)
        if self.tokenizer.current_token() == "void":
            self.process("void", next_prefix)
        else:
            self.process_type(next_prefix)

        self.process(self.tokenizer.identifier(), next_prefix)
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
        self.process_type(next_prefix)
        self.process(self.tokenizer.identifier(), next_prefix)

        while self.tokenizer.current_token() == ",":
            self.process(",", next_prefix)
            self.process_type(next_prefix)
            self.process(self.tokenizer.identifier(), next_prefix)

        self.xml.append(f"{prefix}</parameterList>\r")

    def compile_subroutine_body(self, prefix="") -> None:
        self.xml.append(f"{prefix}<subroutineBody>\r")

        next_prefix = prefix + "  "
        self.process("{", next_prefix)
        while self.tokenizer.current_token() == "var":
            self.compile_var_dec(next_prefix)

        self.compile_statements(next_prefix)
        self.process("}", next_prefix)

        self.xml.append(f"{prefix}</subroutineBody>\r")

    def compile_var_dec(self, prefix="") -> None:
        self.xml.append(f"{prefix}<varDec>\r")
        next_prefix = prefix + "  "
        self.process("var", next_prefix)
        self.process_type(next_prefix)
        self.process_list(self.tokenizer.identifier, next_prefix)
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
                    raise Exception(f"Bad token {self.tokenizer.current_token()}")

        self.xml.append(f"{prefix}</statements>\r")

    def compile_let(self, prefix="") -> None:
        self.xml.append(f"{prefix}<letStatement>\r")

        next_prefix = prefix + "  "
        self.process("let", next_prefix)
        self.process(self.tokenizer.identifier(), next_prefix)
        if self.tokenizer.current_token() == "[":
            self.process("[", next_prefix)
            self.compile_expression(next_prefix)
            self.process("]", next_prefix)

        self.process("=", next_prefix)
        self.compile_expression(next_prefix)
        self.process(";", next_prefix)

        self.xml.append(f"{prefix}</letStatement>\r")

    def compile_if(self, prefix="") -> None:
        self.xml.append(f"{prefix}<ifStatement>\r")

        next_prefix = prefix + "  "
        self.process("if", next_prefix)
        self.process("(", next_prefix)
        self.compile_expression(next_prefix)
        self.process(")", next_prefix)
        self.process("{", next_prefix)
        self.compile_statements(next_prefix)
        self.process("}", next_prefix)

        if self.tokenizer.current_token() == "else":
            self.process("else", next_prefix)
            self.process("{", next_prefix)
            self.compile_statements(next_prefix)
            self.process("}", next_prefix)

        self.xml.append(f"{prefix}</ifStatement>\r")

    def compile_while(self, prefix="") -> None:
        self.xml.append(f"{prefix}<whileStatement>\r")

        next_prefix = prefix + "  "
        self.process("while", next_prefix)
        self.process("(", next_prefix)
        self.compile_expression(next_prefix)
        self.process(")", next_prefix)
        self.process("{", next_prefix)
        self.compile_statements(next_prefix)
        self.process("}", next_prefix)

        self.xml.append(f"{prefix}</whileStatement>\r")

    def compile_do(self, prefix="") -> None:
        self.xml.append(f"{prefix}<doStatement>\r")
        next_prefix = prefix + "  "
        self.process("do", next_prefix)

        self.process(self.tokenizer.identifier(), next_prefix)

        if self.tokenizer.current_token() == "(":
            self.process("(", next_prefix)
            self.compile_expression_list(next_prefix)
            self.process(")", next_prefix)
        else:
            self.process(".", next_prefix)
            self.process(self.tokenizer.identifier(), next_prefix)
            self.process("(", next_prefix)
            self.compile_expression_list(next_prefix)
            self.process(")", next_prefix)

        self.process(";", next_prefix)
        self.xml.append(f"{prefix}</doStatement>\r")

    def compile_return(self, prefix="") -> None:
        self.xml.append(f"{prefix}<returnStatement>\r")
        next_prefix = prefix + "  "
        self.process("return", next_prefix)
        if self.tokenizer.current_token() != ";":
            self.compile_expression(next_prefix)
        self.process(";", next_prefix)
        self.xml.append(f"{prefix}</returnStatement>\r")

    def compile_expression(self, prefix="") -> None:
        self.xml.append(f"{prefix}<expression>\r")

        next_prefix = prefix + "  "
        self.compile_term(next_prefix)

        while self.tokenizer.current_token() in OP:
            self.process(self.tokenizer.symbol(), next_prefix)
            self.compile_term(next_prefix)

        self.xml.append(f"{prefix}</expression>\r")

    def compile_term(self, prefix="") -> None:
        self.xml.append(f"{prefix}<term>\r")

        next_prefix = prefix + "  "

        if (
            self.tokenizer.token_type() in [INT_CONST, STRING_CONST]
            or self.tokenizer.current_token() in KEYWORD_CONST
        ):
            self.process(self.tokenizer.current_token(), next_prefix)
            self.xml.append(f"{prefix}</term>\r")
            return

        if self.tokenizer.current_token() in UNARY_OP:
            self.process(self.tokenizer.current_token(), next_prefix)
            self.compile_term(next_prefix)
            self.xml.append(f"{prefix}</term>\r")
            return

        if self.tokenizer.current_token() == "(":
            self.process("(", next_prefix)
            self.compile_expression(next_prefix)
            self.process(")", next_prefix)
            self.xml.append(f"{prefix}</term>\r")
            return

        self.process(self.tokenizer.identifier(), next_prefix)

        match self.tokenizer.current_token():
            case "(":
                self.process("(", next_prefix)
                self.compile_expression_list(next_prefix)
                self.process(")", next_prefix)
            case "[":
                self.process("[", next_prefix)
                self.compile_expression(next_prefix)
                self.process("]", next_prefix)
            case ".":
                self.process(".", next_prefix)
                self.process(self.tokenizer.identifier(), next_prefix)
                self.process("(", next_prefix)
                self.compile_expression_list(next_prefix)
                self.process(")", next_prefix)
            case _:
                pass

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


# if __name__ == "__main__":
#     tokenizer = JackTokenizer(
#         "/home/sandro/code/nand2tetris/nand2tetris/projects/nand2tetris-starter-py/Test.jack"
#     )
#     analyzer = CompilationXMLEngine(tokenizer)
#
#     print("\n".join(analyzer.xml))
