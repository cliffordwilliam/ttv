import subprocess
from pathlib import Path
from audio import duration_seconds
from config import FPS


def stitch_slide(image_path: str | Path, audio_path: str | Path, output_path: str | Path) -> None:
    image_path = Path(image_path)
    audio_path = Path(audio_path)
    output_path = Path(output_path)

    duration = duration_seconds(audio_path)
    fade_out_start = max(0.0, duration - 0.5)

    vf = f"fade=in:0:15,fade=out:st={fade_out_start:.3f}:d=0.5"

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(image_path),
            "-i", str(audio_path),
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac",
            "-vf", vf,
            "-r", str(FPS),
            "-shortest",
            str(output_path),
        ],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg stitch failed:\n{result.stderr[-2000:]}")


def concatenate(clip_paths: list[str | Path], output_path: str | Path) -> None:
    output_path = Path(output_path)
    concat_list = output_path.parent / "concat.txt"

    with open(concat_list, "w") as f:
        for clip in clip_paths:
            f.write(f"file '{Path(clip).resolve()}'\n")

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(output_path),
        ],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )

    concat_list.unlink()

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg concat failed:\n{result.stderr[-2000:]}")
