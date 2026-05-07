from dataclasses import dataclass, field
from typing import Protocol


class Translator(Protocol):
    def binary_for(self, instruction: str) -> str:
        pass


@dataclass
class BasicJumpTranslator:
    def binary_for(self, jump: str) -> str:
        mask = 0

        if "G" in jump:
            mask |= 1 << 0

        if "E" in jump:
            mask |= 1 << 1

        if "L" in jump:
            mask |= 1 << 2

        if "M" in jump or "N" in jump:
            mask = ~mask & 0b111

        return format(mask, "03b")


@dataclass
class BasicDestTranslator:
    def binary_for(self, dest: str) -> str:
        mask = 0

        if "M" in dest:
            mask |= 1 << 0

        if "D" in dest:
            mask |= 1 << 1

        if "A" in dest:
            mask |= 1 << 2

        return format(mask, "03b")


@dataclass
class BasicCompTranslator:
    def binary_for(self, comp: str) -> str:
        mask = 0

        match comp:
            case "0":
                mask |= 0b101010
            case "1":
                mask |= 0b111111
            case "-1":
                mask |= 0b111010
            case "D":
                mask |= 0b001100
            case "A" | "M":
                mask |= 0b110000
            case "!D":
                mask |= 0b001101
            case "!A" | "!M":
                mask |= 0b110001
            case "-D":
                mask |= 0b001111
            case "-A" | "-M":
                mask |= 0b101010
            case "D+1":
                mask |= 0b011111
            case "A+1" | "M+1":
                mask |= 0b110111
            case "D-1":
                mask |= 0b001110
            case "A-1" | "M-1":
                mask |= 0b110010
            case "D+A" | "D+M":
                mask |= 0b000010
            case "D-A" | "D-M":
                mask |= 0b010011
            case "A-D" | "M-D":
                mask |= 0b000111
            case "D&A" | "D&M":
                mask |= 0b000000
            case "D|A" | "D|M":
                mask |= 0b010101

        if "M" in comp:
            mask |= 1 << 6

        return format(mask, "07b")


@dataclass
class BasicCInstructionTranslator:
    jump_translator: Translator = field(default_factory=BasicJumpTranslator)
    comp_translator: Translator = field(default_factory=BasicCompTranslator)
    dest_translator: Translator = field(default_factory=BasicDestTranslator)

    def dest_from(self, instruction: str) -> str:
        dest_index = instruction.find("=")
        return "" if dest_index == -1 else instruction[:dest_index]

    def jump_from(self, instruction: str) -> str:
        jump_index = instruction.find(";")
        return "" if jump_index == -1 else instruction[jump_index + 1 :]

    def comp_from(self, instruction: str) -> str:
        dest_index = instruction.find("=")
        jump_index = (
            len(instruction) if ";" not in instruction else instruction.find(";")
        )

        return instruction[dest_index + 1 : jump_index]

    def binary_for(self, instruction: str) -> str:
        binary = "111"

        binary += self.comp_translator.binary_for(self.comp_from(instruction))
        binary += self.dest_translator.binary_for(self.dest_from(instruction))
        binary += self.jump_translator.binary_for(self.jump_from(instruction))

        return binary


@dataclass
class BasicAInstructionTranslator:
    def binary_for(self, instruction: str) -> str:
        return format(int(instruction[1:]), "016b")
