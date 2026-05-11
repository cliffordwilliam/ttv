import subprocess
from pathlib import Path

from config import FPS, PAUSE_AFTER_S, PAUSE_BEFORE_S


def video_editor_task_logic(
    drawing_saved_file_path: Path,
    slide_screen_time: float,
    video_saved_file_path: Path,
    voice_saved_file_path: Path | None = None,
) -> None:
    padded_slide_screen_time = PAUSE_BEFORE_S + slide_screen_time + PAUSE_AFTER_S
    fade_out_start_time = padded_slide_screen_time - 0.5
    audio_delay_ms = int(PAUSE_BEFORE_S * 1000)

    # Build the cmd for ffmpeg.

    # Allow output overwrite, input 0 is image, keep input 0 open.
    cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(drawing_saved_file_path)]
    if voice_saved_file_path:
        # Input 1 is audio.
        cmd += ["-i", str(voice_saved_file_path)]
        # Apply delay to audio, set compression algo for audio.
        cmd += [
            "-af",
            f"adelay={audio_delay_ms}|{audio_delay_ms}",
            "-c:a",
            "aac",
        ]
    # Set compression algo for image.
    cmd += ["-c:v", "libx264", "-tune", "stillimage"]
    # Apply fade to image, set FPS, limit image input stream duration.
    cmd += [
        "-vf",
        f"fade=in:st=0:d=0.5,fade=out:st={fade_out_start_time:.3f}:d=0.5",
        "-r",
        str(FPS),
        "-t",
        f"{padded_slide_screen_time:.3f}",
        str(video_saved_file_path),
    ]

    # Run the ffmpeg cmd. This gives up GIL.
    result = _run_cmd(cmd)

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg stitch failed:\n{result.stderr[-2000:]}")


def link_each_saved_videos_into_one_big_video_file(
    video_saved_file_paths: list[Path], absolute_video_output_path: Path
) -> None:
    # Create a todo list for the concat.
    # To concat each small videos into one big video.
    concat_todo_list = absolute_video_output_path.parent / "concat_todo_list.txt"
    with open(concat_todo_list, "w") as f:
        for clip in video_saved_file_paths:
            f.write(f"file '{Path(clip).resolve()}'\n")

    # Allow output overwrite.
    # Use concat demux to read todo file and grab stream from each saved video.
    # Allow absolute path. Set input 0 as todo text file.
    # Merge bytes from individual video into one big video.
    result = _run_cmd(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_todo_list),
            "-c",
            "copy",
            str(absolute_video_output_path),
        ]
    )

    # Delete todo txt file.
    concat_todo_list.unlink()

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
