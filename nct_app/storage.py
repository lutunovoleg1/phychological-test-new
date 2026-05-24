"""Хранилище результатов в SQLite."""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from .models import TestResult

logger = logging.getLogger(__name__)


class ResultsStorage:
    """Хранилище результатов тестов в SQLite."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._initialize()

    def _initialize(self) -> None:
        """Инициализация схемы БД."""
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
            logger.info("База данных инициализирована: %s", self.db_path)

    def save_result(self, result: TestResult) -> None:
        """Сохранение результата теста."""
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
                    result.patient.name,
                    result.patient.age,
                    result.patient.education_years,
                    round(result.total_time_seconds, 2),
                    result.errors_count,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
        logger.info(
            "Результат сохранен: %s, время=%.2fс, ошибки=%d",
            result.patient.name,
            result.total_time_seconds,
            result.errors_count,
        )
