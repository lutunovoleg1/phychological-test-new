"""Движок логики теста NCT."""

import logging
import time

from .config import NUMBERS_COUNT

logger = logging.getLogger(__name__)


class NctEngine:
    """Движок управления состоянием теста."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Сброс состояния движка."""
        self.current_target = 1
        self.errors_count = 0
        self.start_time: float | None = None
        self.finished = False
        logger.debug("Движок сброшен")

    def register_click(self, number: int) -> tuple[bool, float | None]:
        """
        Регистрация клика по числу.

        Returns:
            Кортеж (корректность, время_завершения или None).
        """
        if self.finished:
            return False, None

        if number != self.current_target:
            self.errors_count += 1
            logger.debug("Ошибка: ожидалось %d, получено %d", self.current_target, number)
            return False, None

        if number == 1 and self.start_time is None:
            self.start_time = time.perf_counter()
            logger.debug("Таймер запущен")

        if number == NUMBERS_COUNT:
            self.finished = True
            finish_time = time.perf_counter()
            total_time = finish_time - (self.start_time or finish_time)
            logger.info("Тест завершен за %.2fс, ошибок: %d", total_time, self.errors_count)
            return True, total_time

        self.current_target += 1
        logger.debug("Переход к цели %d", self.current_target)
        return True, None
