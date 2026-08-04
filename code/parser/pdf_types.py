from dataclasses import dataclass
from enum import Enum


class LineType(Enum):
    PAGE = "page"
    FAMILY = "family"
    CULTURE = "culture"
    SECTION = "section"
    ENTRY = "entry"
    UNKNOWN = "unknown"


@dataclass
class Line:
    text: str
    font: str
    size: float
    page: int
    x: float
    y: float