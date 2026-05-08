import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from slides.code import CodeSlide

sample = {
    "type": "code",
    "voice_line": "Here is the main render function.",
    "lang": "python",
    "content": [
        "from PIL import Image",
        "",
        "class ProseSlide(BaseSlide):",
        "    def render(self) -> Image.Image:",
        "        img = self._blank_canvas()    !#",
        "        draw = ImageDraw.Draw(img)",
        "        for line in self.content:",
        "            # draw each line",
        "            draw.text((x, y), line, font=font, fill=color)",
        "        return img    !#",
    ],
}

slide = CodeSlide(sample)
img = slide.render()
img.save("test_code.png")
print(f"Saved test_code.png ({img.size[0]}x{img.size[1]})")
