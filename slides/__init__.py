from schemas import CodeData, ImageData, ProseData, SlideData
from slides.base import BaseSlide
from slides.code import CodeSlide
from slides.image import ImageSlide
from slides.prose import ProseSlide


def make_slide(data: SlideData) -> BaseSlide:
    if isinstance(data, ProseData):
        return ProseSlide(data)
    if isinstance(data, ImageData):
        return ImageSlide(data)
    if isinstance(data, CodeData):
        return CodeSlide(data)
    raise ValueError(f"Unknown slide data type: {type(data).__name__!r}")
