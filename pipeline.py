import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from parser import parse
from slides import make_slide
from audio import synthesize
from stitch import stitch_slide, concatenate


def _render_slide(slide_data: dict, img_path: Path) -> None:
    make_slide(slide_data).render().save(img_path)


def _synthesize_slide(slide_data: dict, wav_path: Path) -> None:
    synthesize(slide_data.get("voice_line", ""), wav_path)


def _stitch_when_ready(
    render_fut: Future, audio_fut: Future,
    img_path: Path, wav_path: Path, mp4_path: Path,
    label: str,
) -> None:
    render_fut.result()
    audio_fut.result()
    print(f"  stitching {label}...")
    stitch_slide(img_path, wav_path, mp4_path)


def run(input_path: str | Path) -> Path:
    input_path = Path(input_path).resolve()
    output_path = input_path.with_suffix(".mp4")
    slides = parse(input_path)
    n = len(slides)

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
            audio_futs = [
                audio_pool.submit(_synthesize_slide, slides[i], wav_paths[i])
                for i in range(n)
            ]
            stitch_futs = [
                stitch_pool.submit(
                    _stitch_when_ready,
                    render_futs[i], audio_futs[i],
                    img_paths[i], wav_paths[i], mp4_paths[i],
                    f"slide {i + 1}/{n}",
                )
                for i in range(n)
            ]

            render_idx = {f: i for i, f in enumerate(render_futs)}
            audio_idx  = {f: i for i, f in enumerate(audio_futs)}

            for f in as_completed(render_idx):
                print(f"  render done: slide {render_idx[f] + 1}/{n}")

            for f in as_completed(audio_idx):
                print(f"  audio done:  slide {audio_idx[f] + 1}/{n}")

            for f in stitch_futs:
                f.result()

        print("Concatenating...")
        concatenate(mp4_paths, output_path)

    print(f"Done: {output_path}")
    return output_path
