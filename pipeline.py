import tempfile
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, Future
from parser import parse
from slides import make_slide
from stitch import stitch_slide, concatenate
from schemas import SlideData
from voice import KokoroProvider


def _render_slide(slide_data: SlideData, img_path: Path) -> None:
    make_slide(slide_data).render().save(img_path)


def _synthesize_slide(
    slide_data: SlideData, wav_path: Path, provider: KokoroProvider
) -> float:
    return provider.synthesize(slide_data.voice_line, wav_path)


def _stitch_when_ready(
    render_fut: Future,
    img_path: Path, duration: float, mp4_path: Path,
    audio_path: Path | None = None,
) -> None:
    render_fut.result()
    stitch_slide(img_path, duration, mp4_path, audio_path)


def run(path: Path, voice: KokoroProvider | None = None) -> Path:
    input_path = path.resolve()
    output_path = input_path.with_suffix(".mp4")
    slides = parse(input_path)
    n = len(slides)
    steps = n * 3 if voice else n * 2
    done = 0
    lock = threading.Lock()

    def _progress(_: Future) -> None:
        nonlocal done
        with lock:
            done += 1
            filled = int(done / steps * 30)
            bar = "█" * filled + "░" * (30 - filled)
            end = "\n" if done == steps else "\r"
            print(f"[{bar}] {done}/{steps}", end=end, flush=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        img_paths = [tmp / f"slide_{i}.png" for i in range(n)]
        wav_paths = [tmp / f"slide_{i}.wav" for i in range(n)]
        mp4_paths = [tmp / f"slide_{i}.mp4" for i in range(n)]

        print(f"Processing {n} slide(s)...")
        with (
            ThreadPoolExecutor() as render_pool,
            ThreadPoolExecutor() as audio_pool,
            ThreadPoolExecutor() as stitch_pool,
        ):
            render_futs = [
                render_pool.submit(_render_slide, slides[i], img_paths[i])
                for i in range(n)
            ]

            if voice:
                audio_futs = [
                    audio_pool.submit(_synthesize_slide, slides[i], wav_paths[i], voice)
                    for i in range(n)
                ]
                for f in audio_futs:
                    f.add_done_callback(_progress)
            else:
                audio_futs = [None] * n

            def _make_stitch_fut(i: int) -> Future:
                if voice:
                    def task():
                        duration = audio_futs[i].result()
                        render_futs[i].result()
                        stitch_slide(img_paths[i], duration, mp4_paths[i], wav_paths[i])
                else:
                    def task():
                        render_futs[i].result()
                        stitch_slide(img_paths[i], slides[i].duration, mp4_paths[i])
                return stitch_pool.submit(task)

            stitch_futs = [_make_stitch_fut(i) for i in range(n)]

            for f in render_futs + stitch_futs:
                f.add_done_callback(_progress)

            for f in stitch_futs:
                f.result()

        print("Concatenating...")
        concatenate(mp4_paths, output_path)

    print(f"Done: {output_path}")
    return output_path
