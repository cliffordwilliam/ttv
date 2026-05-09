from dataclasses import dataclass, field


@dataclass
class SlideData:
    content: list[str] = field(default_factory=list)
    voice_line: str = ""
    duration: float = 0.0

    def __post_init__(self):
        self.duration = float(self.duration)


@dataclass
class ProseData(SlideData):
    pass


@dataclass
class ImageData(SlideData):
    src: str = ""


@dataclass
class CodeData(SlideData):
    lang: str = "text"


REGISTRY: dict[str, type[SlideData]] = {
    "prose": ProseData,
    "image": ImageData,
    "code":  CodeData,
}
