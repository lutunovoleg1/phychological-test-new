"""GUI приложение для NCT теста."""

import logging
from typing import Any

try:
    import tkinter as tk
    from tkinter import messagebox
except ModuleNotFoundError:
    tk = None  # type: ignore[assignment]
    messagebox = None  # type: ignore[assignment]

from .config import (
    ACTIVE_FILL,
    ACTIVE_HIGHLIGHT,
    ACTIVE_OUTLINE,
    ACTIVE_SHADOW,
    ACTIVE_TEXT,
    CANVAS_BG,
    DB_PATH,
    ERROR_FILL,
    ERROR_OUTLINE,
    SELECTED_FILL,
    SELECTED_HIGHLIGHT,
    SELECTED_OUTLINE,
    SELECTED_SHADOW,
    SELECTED_TEXT,
)
from .engine import NctEngine
from .layout import LayoutGenerator
from .models import Circle, TestResult
from .storage import ResultsStorage
from .validators import PatientValidator

logger = logging.getLogger(__name__)


class ElectronicNctApp:
    """Основное GUI приложение."""

    def __init__(self, root: "tk.Tk") -> None:
        self.root = root
        self.root.title("eNCT-A: электронный тест соединения чисел")
        self.root.minsize(760, 640)

        self.storage = ResultsStorage(DB_PATH)
        self.engine = NctEngine()
        self.generator = LayoutGenerator()
        self.validator = PatientValidator()

        self.circles: list[Circle] = []
        self.number_to_items: dict[int, dict[str, int]] = {}

        # Переменные UI
        self.patient_name = tk.StringVar(value="Пациент")
        self.age = tk.StringVar(value="45")
        self.education_years = tk.StringVar(value="12")
        self.status = tk.StringVar(
            value="Заполните данные пациента и нажмите «Новый тест». Таймер стартует по клику на 1."
        )

        self._build_ui()
        self.root.after(100, self.new_test)

    def _build_ui(self) -> None:
        """Построение интерфейса."""
        top_bar = tk.Frame(self.root, padx=10, pady=8)
        top_bar.pack(fill="x")

        self._add_labeled_entry(top_bar, "Пациент/ID", self.patient_name, 18)
        self._add_labeled_entry(top_bar, "Возраст", self.age, 5)
        self._add_labeled_entry(top_bar, "Обучение", self.education_years, 5)

        tk.Button(top_bar, text="Новый тест", command=self.new_test).pack(side=tk.RIGHT, padx=(8, 0))

        self.canvas = tk.Canvas(self.root, bg=CANVAS_BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        bottom_bar = tk.Frame(self.root, padx=10, pady=8)
        bottom_bar.pack(fill="x")

        tk.Label(bottom_bar, textvariable=self.status, anchor="w").pack(side=tk.LEFT, fill="x", expand=True)

    def _add_labeled_entry(
        self, parent: "tk.Frame", label: str, variable: "tk.StringVar", width: int
    ) -> None:
        """Добавление подписанного поля ввода."""
        group = tk.Frame(parent)
        group.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(group, text=label).pack(anchor="w")
        tk.Entry(group, textvariable=variable, width=width).pack(anchor="w")

    def new_test(self) -> None:
        """Инициализация нового теста."""
        name = self.patient_name.get()
        age_str = self.age.get()
        education_str = self.education_years.get()

        is_valid, _, error_msg = self.validator.validate(name, age_str, education_str)
        if not is_valid:
            self.status.set(f"Проверьте данные пациента: {error_msg}")
            logger.warning("Невалидные данные пациента: %s", error_msg)

        self.engine.reset()
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 700)
        height = max(self.canvas.winfo_height(), 500)
        self.circles = self.generator.generate(width, height)
        self.number_to_items.clear()

        for circle in self.circles:
            self._draw_circle(circle)

        self.status.set("Готово. Нажмите 1, затем продолжайте по порядку до 25.")
        logger.info("Новый тест инициирован")

    def _draw_circle(self, circle: Circle) -> None:
        """Отрисовка круга с числом."""
        tag = f"num_{circle.number}"
        x0 = circle.x - circle.radius
        y0 = circle.y - circle.radius
        x1 = circle.x + circle.radius
        y1 = circle.y + circle.radius

        shadow_offset = max(2, int(circle.radius * 0.08))
        shadow_id = self.canvas.create_oval(
            x0 + shadow_offset,
            y0 + shadow_offset,
            x1 + shadow_offset,
            y1 + shadow_offset,
            fill=ACTIVE_SHADOW,
            outline="",
            tags=(tag, "circle_shadow"),
        )
        oval_id = self.canvas.create_oval(
            x0,
            y0,
            x1,
            y1,
            fill=ACTIVE_FILL,
            outline=ACTIVE_OUTLINE,
            width=1,
            tags=(tag, "circle"),
        )
        highlight_radius = circle.radius * 0.52
        highlight_id = self.canvas.create_oval(
            circle.x - highlight_radius,
            circle.y - highlight_radius,
            circle.x + highlight_radius,
            circle.y + highlight_radius,
            fill=ACTIVE_HIGHLIGHT,
            outline="",
            tags=(tag, "circle_highlight"),
        )
        text_id = self.canvas.create_text(
            circle.x,
            circle.y,
            text=str(circle.number),
            fill=ACTIVE_TEXT,
            font=("Segoe UI", max(14, int(circle.radius * 0.78)), "bold"),
            tags=(tag, "number_text"),
        )
        self.number_to_items[circle.number] = {
            "shadow": shadow_id,
            "oval": oval_id,
            "highlight": highlight_id,
            "text": text_id,
        }

    def on_canvas_click(self, event: "tk.Event[Any]") -> None:
        """Обработка клика по холсту."""
        number = self._number_from_click(event.x, event.y)
        if number is None:
            if not self.engine.finished:
                self._register_miss()
            return

        is_correct, total_time = self.engine.register_click(number)
        if not is_correct:
            self._flash_number(number)
            self.root.bell()
            self._update_progress()
            return

        self._fade_number(number)

        if total_time is not None:
            self._finish_test(total_time)
            return

        self._update_progress()

    def _number_from_click(self, x: int, y: int) -> int | None:
        """Определение числа по координатам клика."""
        item_ids = self.canvas.find_overlapping(x, y, x, y)
        for item_id in reversed(item_ids):
            number = self._number_from_item(item_id)
            if number is not None:
                return number

        item_ids = self.canvas.find_withtag("current")
        if not item_ids:
            return None

        return self._number_from_item(item_ids[0])

    def _number_from_item(self, item_id: int) -> int | None:
        """Извлечение номера из тега элемента."""
        for tag in self.canvas.gettags(item_id):
            if tag.startswith("num_"):
                return int(tag.split("_", 1)[1])
        return None

    def _register_miss(self) -> None:
        """Регистрация промаха мимо цели."""
        self.engine.errors_count += 1
        self.root.bell()
        self.status.set(
            f"Промах. Следующая цель: {self.engine.current_target}. Ошибок: {self.engine.errors_count}."
        )

    def _flash_number(self, number: int) -> None:
        """Визуальный эффект ошибки на числе."""
        items = self.number_to_items.get(number)
        if items is None:
            return

        oval_id = items["oval"]
        original_fill = self.canvas.itemcget(oval_id, "fill")
        original_outline = self.canvas.itemcget(oval_id, "outline")
        self.canvas.itemconfig(oval_id, fill=ERROR_FILL, outline=ERROR_OUTLINE)
        self.root.after(200, lambda: self.canvas.itemconfig(oval_id, fill=original_fill, outline=original_outline))

    def _fade_number(self, number: int) -> None:
        """Визуальный эффект завершения числа."""
        items = self.number_to_items[number]
        self.canvas.itemconfig(items["shadow"], fill=SELECTED_SHADOW)
        self.canvas.itemconfig(items["oval"], fill=SELECTED_FILL, outline=SELECTED_OUTLINE)
        self.canvas.itemconfig(items["highlight"], fill=SELECTED_HIGHLIGHT)
        self.canvas.itemconfig(items["text"], fill=SELECTED_TEXT)

    def _update_progress(self) -> None:
        """Обновление статуса прогресса."""
        self.status.set(
            f"Следующая цель: {self.engine.current_target}. Ошибок: {self.engine.errors_count}."
        )

    def _finish_test(self, total_time: float) -> None:
        """Завершение теста и сохранение результата."""
        name = self.patient_name.get()
        age_str = self.age.get()
        education_str = self.education_years.get()

        is_valid, patient, error_msg = self.validator.validate(name, age_str, education_str)
        if not is_valid or patient is None:
            self.status.set(
                f"Тест завершен за {total_time:.2f} с, но результат не сохранен: {error_msg}"
            )
            logger.warning("Результат не сохранён: %s", error_msg)
            return

        result = TestResult(
            patient=patient,
            total_time_seconds=total_time,
            errors_count=self.engine.errors_count,
        )
        self.storage.save_result(result)

        self.status.set(
            f"Финиш: {total_time:.2f} с. Ошибок: {self.engine.errors_count}. Результат сохранен в {DB_PATH.name}."
        )
        if messagebox:
            messagebox.showinfo(
                "Тест завершен",
                f"Время: {total_time:.2f} с\nОшибок: {self.engine.errors_count}\nРезультат сохранен.",
            )
        logger.info("Тест завершён и сохранён")
