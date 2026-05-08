from slides.prose import ProseSlide
from slides.image import ImageSlide
from slides.code import CodeSlide
from slides.base import BaseSlide

_REGISTRY = {
    "prose": ProseSlide,
    "image": ImageSlide,
    "code": CodeSlide,
}


def make_slide(data: dict) -> BaseSlide:
    slide_type = data.get("type", "")
    cls = _REGISTRY.get(slide_type)
    if cls is None:
        raise ValueError(f"Unknown slide type: {slide_type!r}")
    return cls(data)
