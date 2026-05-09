from abc import ABC, abstractmethod
from PIL import Image
from config import RESOLUTION, BACKGROUND_COLOR
from schemas import SlideData


class BaseSlide(ABC):
    def __init__(self, data: SlideData):
        self.data = data

    @abstractmethod
    def render(self) -> Image.Image:
        """Return a rendered PIL Image at the configured resolution."""

    def _blank_canvas(self) -> Image.Image:
        return Image.new("RGB", RESOLUTION, color=BACKGROUND_COLOR)
