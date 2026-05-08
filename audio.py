import subprocess
import wave
import struct
from pathlib import Path
from config import VOICE_MODEL, VOICE_MODEL_DIR, PAUSE_BEFORE_MS, PAUSE_AFTER_MS


def synthesize(voice_line: str, output_path: str | Path) -> None:
    output_path = Path(output_path)
    model_path = Path(VOICE_MODEL_DIR) / f"{VOICE_MODEL}.onnx"
    raw_path = output_path.with_suffix(".raw.wav")

    result = subprocess.run(
        ["piper",
         "--model", str(model_path),
         "--output_file", str(raw_path)],
        input=voice_line,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Piper failed: {result.stderr.strip()}")

    _pad_silence(raw_path, output_path, PAUSE_BEFORE_MS, PAUSE_AFTER_MS)
    raw_path.unlink()


def _pad_silence(src: Path, dst: Path, before_ms: int, after_ms: int) -> None:
    with wave.open(str(src), "rb") as w:
        params = w.getparams()
        frames = w.readframes(w.getnframes())

    sample_rate = params.framerate
    n_channels = params.nchannels
    sampwidth = params.sampwidth

    def silence(ms: int) -> bytes:
        n_frames = int(sample_rate * ms / 1000) * n_channels
        return struct.pack(f"<{n_frames}{'h' if sampwidth == 2 else 'b'}", *([0] * n_frames))

    with wave.open(str(dst), "wb") as w:
        w.setparams(params)
        w.writeframes(silence(before_ms) + frames + silence(after_ms))


def duration_seconds(path: str | Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()
