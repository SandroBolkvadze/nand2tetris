from dataclasses import dataclass
from pathlib import Path

from n2t.infra.io import File

keyword = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]

symbols = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]

@dataclass
class JackTokenizer:
    def __init__(self, path: str) -> None:
        self.token = None; self.is_str = None

        self.content = ""
        for line in File(Path(path)).load():
            self.content += f"{line}\n"

        self.position = 0

    def _align(self) -> bool:
        old_position = self.position

        while self.position < len(self.content):
            if self.content[self.position] in [" ", "\n"]:
                self.position += 1
            elif self.content[self.position: self.position + 2] == "//":
                self.position = self.content.find("\n", self.position) + 1
            elif self.content[self.position: self.position + 2] in ["/*", "/**"]:
                self.position = self.content.find("*/", self.position) + 2
            else:
                break

        return old_position != self.position

    def has_more_tokens(self) -> bool:
        self._align()
        return self.position != len(self.content)

    def advance(self) -> str:
        self._align()

        start = self.position; self.position += 1
        token = self.content[start]

        # if token is string
        if token == "\"":
            self.position = self.content.find("\"", self.position + 1) + 1
            self.token = token; self.is_str = True
            return self.content[start + 1: self.position - 1]

        # advance one character each on each cycle
        while True:
            if self._align() or self.position == len(self.content):
                break
            ch = self.content[self.position]
            if ch == " " or ch in symbols or token in symbols:
                break
            token += ch; self.position += 1

        self.token = token; self.is_str = False

        return token

    def token_type(self) -> str:
        if self.token in keyword:
            return "keyword"
        elif self.token in symbols:
            return "symbol"
        elif self.token.isdigit():
            return "integerConstant"
        elif self.is_str:
            return "stringConstant"
        else:
            return "identifier"

# if __name__ == "__main__":
#     tokenizer = JackTokenizer("/home/sandro/code/nand2tetris/nand2tetris/projects/nand2tetris-starter-py/tests/e2e/jacks_for_analyzer/Square/Main.jack")
#     output    = File(Path("/home/sandro/code/nand2tetris/nand2tetris/projects/nand2tetris-starter-py/tests/e2e/jacks_for_analyzer/Square/MainT.xml"))
#
#     xml = ["<tokens>"]
#     while tokenizer.has_more_tokens():
#         token = tokenizer.advance()
#         type = tokenizer.token_type()
#         xml.append(f"<{type}> {token} </{type}>")
#     xml.append("</tokens>")
#
#     print(xml)
#     output.save(xml)



