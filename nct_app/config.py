"""Конфигурация приложения."""

from pathlib import Path

# Пути
APP_DIR = Path(__file__).resolve().parent.parent
DB_PATH = APP_DIR / "nct_results.db"

# Параметры теста
NUMBERS_COUNT = 25
GRID_SIZE = 5

# Цвета и стили
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

# Валидация данных пациента
MIN_AGE = 1
MAX_AGE = 129
MIN_EDUCATION_YEARS = 0
MAX_EDUCATION_YEARS = 59
