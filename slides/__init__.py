from schemas import SlideData, ProseData, ImageData, CodeData
from slides.prose import ProseSlide
from slides.image import ImageSlide
from slides.code import CodeSlide
from slides.base import BaseSlide


def make_slide(data: SlideData) -> BaseSlide:
    if isinstance(data, ProseData):
        return ProseSlide(data)
    if isinstance(data, ImageData):
        return ImageSlide(data)
    if isinstance(data, CodeData):
        return CodeSlide(data)
    raise ValueError(f"Unknown slide data type: {type(data).__name__!r}")
