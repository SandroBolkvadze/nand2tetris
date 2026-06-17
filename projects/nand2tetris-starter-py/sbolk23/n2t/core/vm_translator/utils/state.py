from dataclasses import dataclass


@dataclass
class VmTranslatorState:
    filename: str = ""

    current_function: str = ""
    current_function_ret_count: int = 0

    total_eq_count: int = 0
    total_gt_count: int = 0
    total_lt_count: int = 0
