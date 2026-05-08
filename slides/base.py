from abc import ABC, abstractmethod
from PIL import Image
from config import RESOLUTION, BACKGROUND_COLOR


class BaseSlide(ABC):
    def __init__(self, data: dict):
        self.voice_line: str = data.get("voice_line", "")
        self.content: list[str] = data.get("content", [])
        self.data = data

    @abstractmethod
    def render(self) -> Image.Image:
        """Return a rendered PIL Image at the configured resolution."""

    def _blank_canvas(self) -> Image.Image:
        return Image.new("RGB", RESOLUTION, color=BACKGROUND_COLOR)
