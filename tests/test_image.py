import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from PIL import Image, ImageDraw
from slides.image import ImageSlide

# generate a sample asset at a non-1080p ratio to exercise the cover logic
sample = Image.new("RGB", (1200, 800), color=(30, 60, 90))
draw = ImageDraw.Draw(sample)
draw.rectangle([(100, 100), (1100, 700)], outline=(100, 180, 255), width=6)
draw.ellipse([(400, 200), (800, 600)], outline=(255, 180, 80), width=6)
draw.line([(0, 0), (1200, 800)], fill=(180, 80, 80), width=4)
draw.line([(1200, 0), (0, 800)], fill=(80, 180, 80), width=4)
sample.save("examples/sample_image.png")

slide = ImageSlide({
    "type": "image",
    "voice_line": "Here is the architecture diagram.",
    "src": "examples/sample_image.png",
    "content": [],
})

img = slide.render()
img.save("test_image.png")
print(f"Saved test_image.png ({img.size[0]}x{img.size[1]})")
