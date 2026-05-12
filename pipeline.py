import tempfile
import threading
from concurrent.futures import Future, ThreadPoolExecutor
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
    KokoroProvider,
    voice_actor_task_logic,
)


class Pipeline:
    def __init__(
        self,
        given_slide_datas: list[SlideData],
        given_absolute_video_output_path: Path,
        kokoro_provider: KokoroProvider | None = None,
    ) -> None:
        # Paths.
        self.absolute_video_output_path = given_absolute_video_output_path

        # Slides.
        self.slide_datas = given_slide_datas
        self.slide_datas_len = len(self.slide_datas)

        # Voice provider.
        self.kokoro_provider = kokoro_provider

        # Loading bar.
        total_thread_groups = 3 if self.kokoro_provider else 2
        self.loading_bar_total_width_dot = self.slide_datas_len * total_thread_groups
        self.loading_bar_progress_width_dot = 0
        self.future_increment_loading_bar_forward_lock = threading.Lock()

        # Temporary save file paths.
        self.drawing_saved_file_paths = []
        self.voice_saved_file_paths = []
        self.video_saved_file_paths = []

        # Threads.
        self.illustrator_threads = []
        self.voice_actor_threads = []
        self.video_editor_threads = []

        # Futures.
        self.illustrator_futures = []
        self.voice_actor_futures = []
        self.video_editor_futures = []

    def run_threads(self):
        # Populate temporary save files.
        with tempfile.TemporaryDirectory() as temporary_directory_string_path:
            temporary_directory_path = Path(temporary_directory_string_path)
            self.drawing_saved_file_paths = [
                temporary_directory_path / f"{i}.png"
                for i in range(self.slide_datas_len)
            ]
            self.voice_saved_file_paths = [
                temporary_directory_path / f"{i}.wav"
                for i in range(self.slide_datas_len)
            ]
            self.video_saved_file_paths = [
                temporary_directory_path / f"{i}.mp4"
                for i in range(self.slide_datas_len)
            ]
            # Populate threads. How much threads you get per group depends on your system.
            with (
                ThreadPoolExecutor() as self.illustrator_threads,
                ThreadPoolExecutor() as self.voice_actor_threads,
                ThreadPoolExecutor() as self.video_editor_threads,
            ):
                # Give tasks to illustrator threads.
                self.illustrator_futures = [
                    self.illustrator_threads.submit(
                        illustrator_task_logic,
                        self.slide_datas[i],
                        self.drawing_saved_file_paths[i],
                    )
                    for i in range(self.slide_datas_len)
                ]

                # Give tasks to voice actor threads if they are present!
                if self.kokoro_provider:
                    self.voice_actor_futures = [
                        self.voice_actor_threads.submit(
                            voice_actor_task_logic,
                            self.slide_datas[i],
                            self.voice_saved_file_paths[i],
                            self.kokoro_provider,
                        )
                        for i in range(self.slide_datas_len)
                    ]

                # Give tasks to video editor threads.
                self.video_editor_futures = [
                    self._give_tasks_to_video_editor_threads(
                        i, self.video_editor_threads
                    )
                    for i in range(self.slide_datas_len)
                ]

                # Give each futures done callback to increment the loading bar.
                for future in (
                    self.illustrator_futures
                    + self.voice_actor_futures
                    + self.video_editor_futures
                ):
                    if future is None:
                        continue
                    future.add_done_callback(self._future_increment_loading_bar_forward)

                # Wait for each video editor future to be done.
                for video_editor_future in self.video_editor_futures:
                    video_editor_future.result()

                # Link step.
                link_each_saved_videos_into_one_big_video_file(
                    self.video_saved_file_paths, self.absolute_video_output_path
                )

            return self.absolute_video_output_path

    def _give_tasks_to_video_editor_threads(
        self, slide_index: int, video_editor_threads: ThreadPoolExecutor
    ):
        if self.kokoro_provider:
            # Voice actor present:
            # - Wait for voice actor and illustrator future to finish.
            # - Voice actor determines screentime.
            def video_editor_task_callback():
                slide_screen_time = self.voice_actor_futures[slide_index].result()
                self.illustrator_futures[slide_index].result()
                video_editor_task_logic(
                    self.drawing_saved_file_paths[slide_index],
                    slide_screen_time,
                    self.video_saved_file_paths[slide_index],
                    self.voice_saved_file_paths[slide_index],
                )

        else:
            # Voice actor absent:
            # - Wait for illustrator future to finish.
            # - Slide data determines screentime.
            def video_editor_task_callback():
                slide_screen_time = self.slide_datas[slide_index].duration
                self.illustrator_futures[slide_index].result()
                video_editor_task_logic(
                    self.drawing_saved_file_paths[slide_index],
                    float(slide_screen_time),
                    self.video_saved_file_paths[slide_index],
                    None,
                )

        return video_editor_threads.submit(video_editor_task_callback)

    def _future_increment_loading_bar_forward(self, _: Future):
        with self.future_increment_loading_bar_forward_lock:
            # Imagine we stack dots in here.
            self.loading_bar_progress_width_dot += 1

            # Get progress fraction in dots scale.
            progress_fraction = (
                self.loading_bar_progress_width_dot / self.loading_bar_total_width_dot
            )

            # Use fraction to stop working in dot scale, and to work in character scale instead.
            # Imagine we stack characters in here now.
            progress_width_char_unit = int(
                progress_fraction * LOADING_BAR_TOTAL_WIDTH_CHAR_UNIT
            )
            empty_width_char_unit = (
                LOADING_BAR_TOTAL_WIDTH_CHAR_UNIT - progress_width_char_unit
            )

            # Knowing we are stacking characters here, we collect the real char/int UTF-8 here.
            filled_characters = progress_width_char_unit * FILLED_BAR_CHARACTER
            empty_characters = empty_width_char_unit * EMPTY_BAR_CHARACTER

            # Here we stack chars to create the loading bar.
            # █ █ █ ░ ░ ░ ░ ░
            bar_characters = filled_characters + empty_characters

            # Resolve to either:
            # - Redraw over the previous bar.
            # - Move cursor to next line.
            end = (
                "\n"
                if self.loading_bar_progress_width_dot
                == self.loading_bar_total_width_dot
                else "\r"
            )

            # Draw the bar!
            print(f"{bar_characters}", end=end, flush=True)
