import tempfile
from pathlib import Path

from config import (
    EMPTY_BAR_CHARACTER,
    FILLED_BAR_CHARACTER,
    LOADING_BAR_TOTAL_WIDTH_CHAR_UNIT,
)
from schemas import SlideData
from thread_task_logics.illustrator_task_logic import illustrator_task_logic
from thread_task_logics.video_editor_task_logic import (
    link_each_saved_videos_into_one_big_video_file,
    video_editor_task_logic,
)
from thread_task_logics.voice_actor_task_logic import (
    ElevenLabsProvider,
    PiperProvider,
    voice_actor_task_logic,
)


class Pipeline:
    def __init__(
        self,
        given_slide_datas: list[SlideData],
        given_absolute_video_output_path: Path,
        provider: ElevenLabsProvider | PiperProvider | None = None,
    ) -> None:
        self.absolute_video_output_path = given_absolute_video_output_path
        self.slide_datas = given_slide_datas
        self.slide_datas_len = len(self.slide_datas)
        self.provider = provider

        total_steps = self.slide_datas_len * (3 if self.provider else 2)
        self.loading_bar_total_steps = total_steps
        self.loading_bar_progress = 0

    def run_threads(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            suffix = self.provider.audio_suffix if self.provider else ".wav"
            drawing_paths = [tmp / f"{i}.png"     for i in range(self.slide_datas_len)]
            voice_paths   = [tmp / f"{i}{suffix}" for i in range(self.slide_datas_len)]
            video_paths   = [tmp / f"{i}.mp4"     for i in range(self.slide_datas_len)]

            # Phase 1: draw all slides — bail before touching any voice API if this fails.
            for i in range(self.slide_datas_len):
                illustrator_task_logic(self.slide_datas[i], drawing_paths[i])
                self._tick()

            # Phase 2: voice all slides.
            durations = []
            for i in range(self.slide_datas_len):
                if self.provider:
                    prev = self.slide_datas[i - 1].voice_line if i > 0 else None
                    nxt  = self.slide_datas[i + 1].voice_line if i < self.slide_datas_len - 1 else None
                    duration = voice_actor_task_logic(
                        self.slide_datas[i],
                        voice_paths[i],
                        self.provider,
                        prev,
                        nxt,
                    )
                    self._tick()
                else:
                    duration = float(self.slide_datas[i].duration)
                durations.append(duration)

            # Phase 3: stitch each clip then concat.
            for i in range(self.slide_datas_len):
                video_editor_task_logic(
                    drawing_paths[i],
                    durations[i],
                    video_paths[i],
                    voice_paths[i] if self.provider else None,
                    self.slide_datas[i].transition_in,
                    self.slide_datas[i].transition_out,
                )
                self._tick()

            link_each_saved_videos_into_one_big_video_file(
                video_paths, self.absolute_video_output_path
            )

        return self.absolute_video_output_path

    def _tick(self):
        self.loading_bar_progress += 1
        progress_fraction = self.loading_bar_progress / self.loading_bar_total_steps
        progress_width = int(progress_fraction * LOADING_BAR_TOTAL_WIDTH_CHAR_UNIT)
        empty_width = LOADING_BAR_TOTAL_WIDTH_CHAR_UNIT - progress_width
        bar = FILLED_BAR_CHARACTER * progress_width + EMPTY_BAR_CHARACTER * empty_width
        end = "\n" if self.loading_bar_progress == self.loading_bar_total_steps else "\r"
        print(bar, end=end, flush=True)
