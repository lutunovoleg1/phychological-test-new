import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import PatientData, TestResult


class ResultsStorage:
    """Хранилище результатов тестирования на основе SQLite."""

    def __init__(self, db_filename: str = "results.db"):
        """
        Инициализация хранилища.

        Путь к БД определяется относительно исполняемого файла (для релиза)
        или корня проекта (для разработки), если передано только имя файла.
        Если передан полный путь (например, из тестов), используется он.
        """
        import sys

        db_path = Path(db_filename)

        # Если передано только имя файла, определяем путь относительно базы
        if not db_path.is_absolute():
            if getattr(sys, 'frozen', False):
                # Запуск из скомпилированного exe (PyInstaller)
                base_dir = Path(sys.executable).parent
            else:
                # Запуск из исходного кода
                base_dir = Path(__file__).resolve().parent.parent
            
            self.db_path = base_dir / db_filename
        else:
            # Используется переданный абсолютный путь (для тестов)
            self.db_path = db_path

        # Инициализация соединения и создание таблиц
        self.conn = sqlite3.connect(str(self.db_path))
        self._create_schema()

    def _create_schema(self):
        """Создание схемы базы данных, если она не существует."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                patient_age INTEGER NOT NULL,
                patient_education INTEGER NOT NULL,
                total_time_seconds REAL NOT NULL,
                errors_count INTEGER NOT NULL,
                test_date TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def save_result(self, result: TestResult) -> None:
        """Сохранение результата тестирования в базу данных."""
        cursor = self.conn.cursor()
        
        # Безопасное получение даты: используем дату из результата или текущую
        test_date = result.test_date if hasattr(result, 'test_date') and result.test_date else datetime.now()
        
        cursor.execute(
            """
            INSERT INTO results (
                patient_name, patient_age, patient_education,
                total_time_seconds, errors_count, test_date
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                result.patient.name,
                result.patient.age,
                result.patient.education_years,
                round(result.total_time_seconds, 2),  # Округляем для чистоты данных
                result.errors_count,
                test_date.isoformat(),
            ),
        )
        self.conn.commit()

    def get_all_results(self) -> List[TestResult]:
        """Получение всех сохраненных результатов."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT patient_name, patient_age, patient_education, "
            "total_time_seconds, errors_count, test_date FROM results"
        )
        rows = cursor.fetchall()

        results = []
        for row in rows:
            patient = PatientData(
                name=row[0], age=row[1], education_years=row[2]
            )
            test_result = TestResult(
                patient=patient,
                total_time_seconds=row[3],
                errors_count=row[4],
                test_date=datetime.fromisoformat(row[5]),
            )
            results.append(test_result)
        return results

    def close(self):
        """Закрытие соединения с базой данных."""
        if self.conn:
            self.conn.close()