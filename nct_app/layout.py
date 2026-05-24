"""Генерация раскладки чисел."""

import random
from dataclasses import dataclass

from .config import GRID_SIZE, NUMBERS_COUNT
from .models import Circle


@dataclass
class LayoutConfig:
    """Конфигурация генерации раскладки."""

    margin_ratio: float = 0.04
    min_margin: int = 24
    radius_ratio: float = 0.22
    jitter_offset: int = 6


class LayoutGenerator:
    """Генератор случайной раскладки кругов с числами."""

    def __init__(self, config: LayoutConfig | None = None) -> None:
        self.config = config or LayoutConfig()

    def generate(self, width: int, height: int) -> list[Circle]:
        """
        Генерация раскладки кругов.

        Args:
            width: Ширина холста в пикселях.
            height: Высота холста в пикселях.

        Returns:
            Список объектов Circle с координатами и радиусом.
        """
        margin = max(
            self.config.min_margin,
            min(width, height) * self.config.margin_ratio,
        )
        usable_width = width - margin * 2
        usable_height = height - margin * 2
        cell_width = usable_width / GRID_SIZE
        cell_height = usable_height / GRID_SIZE
        radius = max(18, min(cell_width, cell_height) * self.config.radius_ratio)
        max_dx = max(0, cell_width / 2 - radius - self.config.jitter_offset)
        max_dy = max(0, cell_height / 2 - radius - self.config.jitter_offset)

        numbers = list(range(1, NUMBERS_COUNT + 1))
        random.shuffle(numbers)

        circles: list[Circle] = []
        for index, number in enumerate(numbers):
            row, column = divmod(index, GRID_SIZE)
            base_x = margin + column * cell_width + cell_width / 2
            base_y = margin + row * cell_height + cell_height / 2
            x = base_x + random.uniform(-max_dx, max_dx)
            y = base_y + random.uniform(-max_dy, max_dy)
            circles.append(Circle(number=number, x=x, y=y, radius=radius))

        return circles
