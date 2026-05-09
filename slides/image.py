from PIL import Image
from pathlib import Path
from slides.base import BaseSlide
from schemas import ImageData
from config import RESOLUTION


class ImageSlide(BaseSlide):
    def __init__(self, data: ImageData):
        super().__init__(data)
        self.data: ImageData = data

    def render(self) -> Image.Image:
        src = self.data.src
        path = Path(src)

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {src}")

        source = Image.open(path).convert("RGB")
        return _cover(source, RESOLUTION)


def _cover(img: Image.Image, size: tuple) -> Image.Image:
    target_w, target_h = size
    src_w, src_h = img.size

    scale = max(target_w / src_w, target_h / src_h)
    new_w = round(src_w * scale)
    new_h = round(src_h * scale)

    img = img.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))
