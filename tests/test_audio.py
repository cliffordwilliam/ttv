import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from audio import synthesize, duration_seconds

out = "test_audio.wav"
synthesize("This slide introduces the topic of text to video compilation.", out)
duration = duration_seconds(out)
print(f"Saved {out} — duration: {duration:.2f}s")
print(f"  (600ms silence before + TTS + 600ms silence after)")
