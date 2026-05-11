import json
import subprocess
import urllib.request
from pathlib import Path

from schemas import SlideData


class KokoroProvider:
    def __init__(self, url: str, voice: str = "af_heart"):
        self.url = url.rstrip("/")
        self.voice = voice


def voice_actor_task_logic(
    slide_data: SlideData, wav_path: Path, provider: KokoroProvider
) -> float:
    payload = json.dumps(
        {
            "model": "kokoro",
            "input": slide_data.voice_line,
            "voice": provider.voice,
            "response_format": "wav",
        }
    ).encode()
    req = urllib.request.Request(
        f"{provider.url}/v1/audio/speech",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        wav_path.write_bytes(resp.read())
    return _audio_duration(wav_path)


def _audio_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr.strip()}")
    return float(result.stdout.strip())
