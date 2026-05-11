from pathlib import Path

from schemas import SlideData
from slides import make_slide


def illustrator_task_logic(slide_data: SlideData, img_path: Path) -> None:
    make_slide(slide_data).render().save(img_path)
