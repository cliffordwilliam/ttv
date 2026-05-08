import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from slides.prose import ProseSlide

sample = {
    "type": "prose",
    "voice_line": "This slide introduces the topic.",
    "content": [
        "# Welcome to ttv",
        "## A text-to-video compiler",
        "This is the first paragraph. It contains a long sentence that should wrap gracefully within the canvas boundaries without overflowing off the right edge of the screen.",
        "",
        "This is the second paragraph, separated by a blank line. Each paragraph flows independently and the gap between them follows the Tailwind prose spacing.",
        "### How it works",
        "- Text goes in",
        "- Video comes out",
        "- Like a compiler for presentations but this bullet point has a much longer description to test wrapping inside list items too",
        "1. Parse the input file",
        "2. Render each slide",
        "3. Stitch into a video",
    ],
}

slide = ProseSlide(sample)
img = slide.render()
img.save("test_prose.png")
print(f"Saved test_prose.png ({img.size[0]}x{img.size[1]})")
