from __future__ import annotations

import random
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import messagebox
except ModuleNotFoundError:
    tk = None
    messagebox = None


APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "nct_results.db"
NUMBERS_COUNT = 25
GRID_SIZE = 5
CANVAS_BG = "#f3f6fb"
ACTIVE_FILL = "#38bdf8"
ACTIVE_OUTLINE = "#0284c7"
ACTIVE_TEXT = "#082f49"
ACTIVE_SHADOW = "#cbd5e1"
ACTIVE_HIGHLIGHT = "#bae6fd"
SELECTED_FILL = "#e5e7eb"
SELECTED_OUTLINE = "#cbd5e1"
SELECTED_TEXT = "#94a3b8"
SELECTED_SHADOW = "#edf2f7"
SELECTED_HIGHLIGHT = "#f8fafc"
ERROR_FILL = "#fb7185"
ERROR_OUTLINE = "#be123c"


@dataclass(frozen=True)
class Circle:
    number: int
    x: float
    y: float
    radius: float


class ResultsStorage:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.initialize()

    def initialize(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    education_years INTEGER NOT NULL,
                    total_time_seconds REAL NOT NULL,
                    errors_count INTEGER NOT NULL,
                    test_date TEXT NOT NULL
                )
                """
            )

    def save_result(
        self,
        patient_name: str,
        age: int,
        education_years: int,
        total_time_seconds: float,
        errors_count: int,
    ) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO test_results (
                    patient_name,
                    age,
                    education_years,
                    total_time_seconds,
                    errors_count,
                    test_date
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    patient_name,
                    age,
                    education_years,
                    round(total_time_seconds, 2),
                    errors_count,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )


class NctEngine:
    def __init__(self) -> None:
        self.current_target = 1
        self.errors_count = 0
        self.start_time: float | None = None
        self.finished = False

    def reset(self) -> None:
        self.current_target = 1
        self.errors_count = 0
        self.start_time = None
        self.finished = False

    def register_click(self, number: int) -> tuple[bool, float | None]:
        if self.finished:
            return False, None

        if number != self.current_target:
            self.errors_count += 1
            return False, None

        if number == 1 and self.start_time is None:
            self.start_time = time.perf_counter()

        if number == NUMBERS_COUNT:
            self.finished = True
            finish_time = time.perf_counter()
            total_time = finish_time - (self.start_time or finish_time)
            return True, total_time

        self.current_target += 1
        return True, None


class LayoutGenerator:
    def generate(self, width: int, height: int) -> list[Circle]:
        margin = max(24, min(width, height) * 0.04)
        usable_width = width - margin * 2
        usable_height = height - margin * 2
        cell_width = usable_width / GRID_SIZE
        cell_height = usable_height / GRID_SIZE
        radius = max(18, min(cell_width, cell_height) * 0.22)
        max_dx = max(0, cell_width / 2 - radius - 6)
        max_dy = max(0, cell_height / 2 - radius - 6)

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


class ElectronicNctApp:
    def __init__(self, root: "tk.Tk") -> None:
        self.root = root
        self.root.title("eNCT-A: электронный тест соединения чисел")
        self.root.minsize(760, 640)

        self.storage = ResultsStorage(DB_PATH)
        self.engine = NctEngine()
        self.generator = LayoutGenerator()
        self.circles: list[Circle] = []
        self.number_to_items: dict[int, dict[str, int]] = {}

        self.patient_name = tk.StringVar(value="Пациент")
        self.age = tk.StringVar(value="45")
        self.education_years = tk.StringVar(value="12")
        self.status = tk.StringVar(value="Заполните данные пациента и нажмите «Новый тест». Таймер стартует по клику на 1.")

        self._build_ui()
        self.root.after(100, self.new_test)

    def _build_ui(self) -> None:
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

    def _add_labeled_entry(self, parent: "tk.Frame", label: str, variable: "tk.StringVar", width: int) -> None:
        group = tk.Frame(parent)
        group.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(group, text=label).pack(anchor="w")
        tk.Entry(group, textvariable=variable, width=width).pack(anchor="w")

    def new_test(self) -> None:
        if not self._validate_patient_data(show_errors=False):
            self.status.set("Проверьте данные пациента: возраст и годы обучения должны быть целыми числами.")

        self.engine.reset()
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 700)
        height = max(self.canvas.winfo_height(), 500)
        self.circles = self.generator.generate(width, height)
        self.number_to_items.clear()

        for circle in self.circles:
            self._draw_circle(circle)

        self.status.set("Готово. Нажмите 1, затем продолжайте по порядку до 25.")

    def _draw_circle(self, circle: Circle) -> None:
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

    def on_canvas_click(self, event) -> None:
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
        for tag in self.canvas.gettags(item_id):
            if tag.startswith("num_"):
                return int(tag.split("_", 1)[1])

        return None

    def _register_miss(self) -> None:
        self.engine.errors_count += 1
        self.root.bell()
        self.status.set(
            f"Промах. Следующая цель: {self.engine.current_target}. Ошибок: {self.engine.errors_count}."
        )

    def _flash_number(self, number: int) -> None:
        items = self.number_to_items.get(number)
        if items is None:
            return

        oval_id = items["oval"]
        original_fill = self.canvas.itemcget(oval_id, "fill")
        original_outline = self.canvas.itemcget(oval_id, "outline")
        self.canvas.itemconfig(oval_id, fill=ERROR_FILL, outline=ERROR_OUTLINE)
        self.root.after(200, lambda: self.canvas.itemconfig(oval_id, fill=original_fill, outline=original_outline))

    def _fade_number(self, number: int) -> None:
        items = self.number_to_items[number]
        self.canvas.itemconfig(items["shadow"], fill=SELECTED_SHADOW)
        self.canvas.itemconfig(items["oval"], fill=SELECTED_FILL, outline=SELECTED_OUTLINE)
        self.canvas.itemconfig(items["highlight"], fill=SELECTED_HIGHLIGHT)
        self.canvas.itemconfig(items["text"], fill=SELECTED_TEXT)

    def _update_progress(self) -> None:
        self.status.set(
            f"Следующая цель: {self.engine.current_target}. Ошибок: {self.engine.errors_count}."
        )

    def _finish_test(self, total_time: float) -> None:
        if not self._validate_patient_data(show_errors=True):
            self.status.set(
                f"Тест завершен за {total_time:.2f} с, но результат не сохранен: исправьте данные пациента."
            )
            return

        self.storage.save_result(
            patient_name=self.patient_name.get().strip(),
            age=int(self.age.get()),
            education_years=int(self.education_years.get()),
            total_time_seconds=total_time,
            errors_count=self.engine.errors_count,
        )
        self.status.set(
            f"Финиш: {total_time:.2f} с. Ошибок: {self.engine.errors_count}. Результат сохранен в {DB_PATH.name}."
        )
        messagebox.showinfo(
            "Тест завершен",
            f"Время: {total_time:.2f} с\nОшибок: {self.engine.errors_count}\nРезультат сохранен.",
        )

    def _validate_patient_data(self, show_errors: bool) -> bool:
        patient_name = self.patient_name.get().strip()
        try:
            age = int(self.age.get())
            education_years = int(self.education_years.get())
        except ValueError:
            if show_errors:
                messagebox.showerror("Ошибка данных", "Возраст и годы обучения должны быть целыми числами.")
            return False

        is_valid = bool(patient_name) and 0 < age < 130 and 0 <= education_years < 60
        if show_errors and not is_valid:
            messagebox.showerror("Ошибка данных", "Заполните ID пациента, возраст и годы обучения корректно.")
        return is_valid


def main() -> None:
    if tk is None:
        raise SystemExit(
            "Для запуска GUI нужен Python с модулем tkinter/Tcl-Tk. "
            "Переустановите Python с опцией Tcl/Tk или запустите приложение в окружении, где tkinter доступен."
        )

    root = tk.Tk()
    ElectronicNctApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
