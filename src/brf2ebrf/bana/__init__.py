"""BANA specific components for processing BRF."""
import json
from enum import Enum
import string

from brf2ebrf.parser import DetectionResult

_BRL_WHITESPACE = string.whitespace + "\u2800"


class PageNumberPosition(Enum):
    """The position of a page number on the page."""
    NONE = 0
    TOP_LEFT = 2
    TOP_RIGHT = 3
    BOTTOM_LEFT = 4
    BOTTOM_RIGHT = 5

    def is_top(self) -> bool:
        """Is the page number at the top of the page."""
        return self.value.bit_length() == 2

    def is_left(self) -> bool:
        """Is the page number at the left of the page."""
        return self.value.bit_count() == 1

    def is_bottom(self) -> bool:
        """Is the page number at the bottom of the page."""
        return self.value.bit_length() == 3

    def is_right(self) -> bool:
        """Is the page number at the right of the page."""
        return self.value.bit_count() == 2


def _find_page_number(page_content: str, number_position: PageNumberPosition, cells_per_line: int, lines_per_page: int,
                      separator: str) -> tuple[str, str]:
    if number_position:
        lines = page_content.splitlines()
        line_index = 0 if number_position.is_top() else (lines_per_page - 1)
        if len(lines) > line_index:
            line = lines[line_index]
            left = number_position.is_left()
            if left or len(line) >= cells_per_line:
                parted = line.partition(separator) if left else line.rpartition(separator)
                line, page_num = (parted[2].lstrip(_BRL_WHITESPACE), parted[0]) if left else (
                    parted[0].rstrip(_BRL_WHITESPACE), parted[2])
                if parted[1] and page_num:
                    lines[line_index] = line
                    return "\n".join(lines), page_num
    return page_content, ""


def create_braille_page_detector(number_position: PageNumberPosition = PageNumberPosition.NONE,
                                 cells_per_line: int = 40, lines_per_page: int = 25, separator: str = "   "):
    """Factory function to create a detector for Braille page numbers."""
    def detect_braille_page_number(text: str, cursor: int, state: str, output_text: str) -> DetectionResult:
        if state == "StartBraillePage":
            end_of_page = text.find("\f", cursor)
            page_content, new_cursor = (text[cursor:end_of_page], end_of_page + 1) if end_of_page >= 0 else (
                text[cursor:], len(text))
            page_content, page_num = _find_page_number(page_content, number_position, cells_per_line,
                                                       lines_per_page, separator)
            number_data = {"Number": page_num} if page_num else {}
            page_cmd = json.dumps({"BraillePage": number_data})
            output = f"\ue000{page_cmd}\ue001{page_content}"
            return DetectionResult(cursor=new_cursor, state=state, confidence=1.0, text=output_text + output)
        return DetectionResult(cursor + 1, state, 0.0, output_text + text[cursor])

    return detect_braille_page_number
