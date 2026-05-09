import subprocess
from pathlib import Path
from config import FPS, PAUSE_BEFORE_S, PAUSE_AFTER_S


def stitch_slide(
    image_path: str | Path,
    duration: float,
    output_path: str | Path,
    audio_path: str | Path | None = None,
) -> None:
    image_path = Path(image_path)
    output_path = Path(output_path)

    total = PAUSE_BEFORE_S + duration + PAUSE_AFTER_S
    fade_out_start = max(0.0, total - 0.5)
    vf = f"fade=in:0:15,fade=out:st={fade_out_start:.3f}:d=0.5"

    delay_ms = int(PAUSE_BEFORE_S * 1000)
    cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(image_path)]
    if audio_path:
        cmd += ["-i", str(audio_path)]
        cmd += [
            "-filter_complex", f"[1:a]adelay={delay_ms}|{delay_ms}[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac",
        ]
    else:
        cmd += ["-c:v", "libx264", "-tune", "stillimage"]
    cmd += ["-vf", vf, "-r", str(FPS), "-t", f"{total:.3f}", str(output_path)]

    result = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True)

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
