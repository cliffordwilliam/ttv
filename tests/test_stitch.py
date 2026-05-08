import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from stitch import stitch_slide

stitch_slide("test_prose.png", "test_audio.wav", "test_slide.mp4")
print("Saved test_slide.mp4 — play it back to verify fades and timing.")
