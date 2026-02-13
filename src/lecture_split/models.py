from dataclasses import dataclass, field


@dataclass
class SlideText:
    page_number: int
    text: str


@dataclass
class Section:
    title: str
    start_page: int
    end_page: int
    summary: str


@dataclass
class LecturePlan:
    lecture_title: str
    sections: list[Section] = field(default_factory=list)
