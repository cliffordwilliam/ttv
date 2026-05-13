from dataclasses import dataclass, field


@dataclass
class SlideData:
    content: list[str] = field(default_factory=list)
    voice_line: str = ""
    duration: str = ""


@dataclass
class ImageData(SlideData):
    src: str = ""


@dataclass
class CodeData(SlideData):
    lang: str = "text"


REGISTRY: dict[str, type[SlideData]] = {
    "image": ImageData,
    "code": CodeData,
}
