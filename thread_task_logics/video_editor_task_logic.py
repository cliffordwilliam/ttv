import subprocess
from pathlib import Path

from config import FPS, PAUSE_AFTER_S, PAUSE_BEFORE_S


def video_editor_task_logic(
    drawing_saved_file_path: Path,
    slide_screen_time: float,
    video_saved_file_path: Path,
    voice_saved_file_path: Path | None = None,
    transition_in: str = "fade",
    transition_out: str = "fade",
) -> None:
    cut_in = transition_in == "cut"
    cut_out = transition_out == "cut"

    before = 0.0 if cut_in else PAUSE_BEFORE_S
    after = 0.0 if cut_out else PAUSE_AFTER_S
    clip_duration = before + slide_screen_time + after
    audio_delay_ms = int(before * 1000)

    # Build the cmd for ffmpeg.

    # Allow output overwrite, input 0 is image, keep input 0 open and demux flow it at 60 fps.
    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-framerate",
        str(FPS),
        "-i",
        str(drawing_saved_file_path),
    ]

    if voice_saved_file_path:
        # Input 1 is audio.
        cmd += ["-i", str(voice_saved_file_path)]
        audio_filters = []
        if not cut_in:
            audio_filters.append(f"adelay={audio_delay_ms}|{audio_delay_ms}")
        # Pad silence to fill the full clip duration so audio and video tracks
        # are the same length — prevents PTS discontinuities at concat boundaries.
        audio_filters.append(f"apad=whole_dur={clip_duration:.3f}")
        cmd += ["-af", ",".join(audio_filters), "-c:a", "aac"]

    fade_filters = []
    if not cut_in:
        fade_filters.append("fade=in:st=0:d=0.5")
    if not cut_out:
        fade_filters.append(f"fade=out:st={clip_duration - 0.5:.3f}:d=0.5")
    if fade_filters:
        cmd += ["-vf", ",".join(fade_filters)]
    cmd += ["-c:v", "libx264", "-tune", "stillimage"]

    # Set mux FPS and its duration to emit stop upstream.
    cmd += [
        "-r",
        str(FPS),
        "-t",
        f"{clip_duration:.3f}",
        str(video_saved_file_path),
    ]

    # Run the ffmpeg cmd. This gives up GIL.
    result = _run_cmd(cmd)

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg stitch failed:\n{result.stderr[-2000:]}")


def link_each_saved_videos_into_one_big_video_file(
    video_saved_file_paths: list[Path], absolute_video_output_path: Path
) -> None:
    # Prepare paths for concat demux.
    saved_video_paths = absolute_video_output_path.parent / "saved_video_paths.txt"
    with open(saved_video_paths, "w") as f:
        for clip in video_saved_file_paths:
            f.write(f"file '{Path(clip).resolve()}'\n")

    # Allow output overwrite.
    # Concat demux reads absolute path and make one big stream for each video files.
    # Keep packets compressed and just bring them togehter in mux.
    result = _run_cmd(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(saved_video_paths),
            "-c",
            "copy",
            str(absolute_video_output_path),
        ]
    )

    # Delete txt file.
    saved_video_paths.unlink()

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg concat failed:\n{result.stderr[-2000:]}")


def _run_cmd(given_cmd: list[str]):
    # Run given command.
    # Set subprocess stdin to null so it wont hang on prompt asking.
    # Capture other file descriptors like stderr.
    # Decode subprocess bytes output as utf8 string.
    return subprocess.run(
        given_cmd, stdin=subprocess.DEVNULL, capture_output=True, encoding="utf-8"
    )
