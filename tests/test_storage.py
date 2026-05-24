"""Тесты для хранилища результатов."""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from nct_app.storage import ResultsStorage
from nct_app.models import PatientData, TestResult


class TestResultsStorage:
    """Тесты для ResultsStorage."""

    @pytest.fixture
    def temp_db(self):
        """Создание временной БД для тестов."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)
        
        yield db_path
        
        # Очистка после теста
        if db_path.exists():
            try:
                db_path.unlink()
            except PermissionError:
                # На Windows файл может быть заблокирован, игнорируем
                pass

    @pytest.fixture
    def storage(self, temp_db):
        """Создание хранилища с временной БД."""
        return ResultsStorage(temp_db)

    def test_storage_initialization(self, temp_db):
        """Проверка инициализации хранилища."""
        storage = ResultsStorage(temp_db)
        
        assert storage.db_path == temp_db
        assert temp_db.exists()

    def test_database_schema_created(self, temp_db):
        """Проверка создания схемы БД."""
        storage = ResultsStorage(temp_db)
        
        # Проверяем существование таблицы
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='test_results'"
            )
            result = cursor.fetchone()
            
        assert result is not None
        assert result[0] == 'test_results'

    def test_save_result(self, storage):
        """Проверка сохранения результата."""
        patient = PatientData(name="Тестовый Пациент", age=40, education_years=15)
        result = TestResult(patient=patient, total_time_seconds=45.67, errors_count=2)
        
        storage.save_result(result)
        
        # Проверяем запись в БД
        with sqlite3.connect(storage.db_path) as conn:
            cursor = conn.execute(
                "SELECT patient_name, age, education_years, total_time_seconds, errors_count FROM test_results"
            )
            row = cursor.fetchone()
        
        assert row is not None
        assert row[0] == "Тестовый Пациент"
        assert row[1] == 40
        assert row[2] == 15
        assert abs(row[3] - 45.67) < 0.01  # Округление до 2 знаков
        assert row[4] == 2

    def test_save_multiple_results(self, storage):
        """Проверка сохранения нескольких результатов."""
        patients = [
            PatientData(name="Пациент 1", age=30, education_years=12),
            PatientData(name="Пациент 2", age=50, education_years=16),
            PatientData(name="Пациент 3", age=25, education_years=10),
        ]
        
        for i, patient in enumerate(patients):
            result = TestResult(
                patient=patient,
                total_time_seconds=30.0 + i * 10,
                errors_count=i
            )
            storage.save_result(result)
        
        # Проверяем количество записей
        with sqlite3.connect(storage.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM test_results")
            count = cursor.fetchone()[0]
        
        assert count == 3

    def test_result_rounding(self, storage):
        """Проверка округления времени."""
        patient = PatientData(name="Тест", age=35, education_years=14)
        result = TestResult(patient=patient, total_time_seconds=123.456789, errors_count=0)
        
        storage.save_result(result)
        
        with sqlite3.connect(storage.db_path) as conn:
            cursor = conn.execute("SELECT total_time_seconds FROM test_results")
            saved_time = cursor.fetchone()[0]
        
        # Время должно быть округлено до 2 знаков
        assert saved_time == 123.46

    def test_result_with_zero_errors(self, storage):
        """Проверка сохранения результата без ошибок."""
        patient = PatientData(name="БезОшибок", age=28, education_years=18)
        result = TestResult(patient=patient, total_time_seconds=25.0, errors_count=0)
        
        storage.save_result(result)
        
        with sqlite3.connect(storage.db_path) as conn:
            cursor = conn.execute("SELECT errors_count FROM test_results WHERE patient_name='БезОшибок'")
            errors = cursor.fetchone()[0]
        
        assert errors == 0

    def test_result_with_many_errors(self, storage):
        """Проверка сохранения результата с большим количеством ошибок."""
        patient = PatientData(name="МногоОшибок", age=60, education_years=8)
        result = TestResult(patient=patient, total_time_seconds=120.0, errors_count=50)
        
        storage.save_result(result)
        
        with sqlite3.connect(storage.db_path) as conn:
            cursor = conn.execute("SELECT errors_count FROM test_results WHERE patient_name='МногоОшибок'")
            errors = cursor.fetchone()[0]
        
        assert errors == 50

    def test_database_persistence(self, temp_db):
        """Проверка сохранения данных между подключениями."""
        patient = PatientData(name="Персистентность", age=45, education_years=13)
        result = TestResult(patient=patient, total_time_seconds=55.5, errors_count=3)
        
        # Сохраняем результат
        storage1 = ResultsStorage(temp_db)
        storage1.save_result(result)
        
        # Создаём новое подключение и проверяем данные
        storage2 = ResultsStorage(temp_db)
        
        with sqlite3.connect(storage2.db_path) as conn:
            cursor = conn.execute("SELECT patient_name FROM test_results")
            row = cursor.fetchone()
        
        assert row is not None
        assert row[0] == "Персистентность"

    def test_special_characters_in_name(self, storage):
        """Проверка имён со спецсимволами."""
        patient = PatientData(name="Иванов-Петров И.И. (тест)", age=33, education_years=11)
        result = TestResult(patient=patient, total_time_seconds=40.0, errors_count=1)
        
        storage.save_result(result)
        
        with sqlite3.connect(storage.db_path) as conn:
            cursor = conn.execute("SELECT patient_name FROM test_results")
            name = cursor.fetchone()[0]
        
        assert name == "Иванов-Петров И.И. (тест)"

    def test_unicode_names(self, storage):
        """Проверка имён в Unicode."""
        patient = PatientData(name="田中太郎", age=55, education_years=16)
        result = TestResult(patient=patient, total_time_seconds=60.0, errors_count=0)
        
        storage.save_result(result)
        
        with sqlite3.connect(storage.db_path) as conn:
            cursor = conn.execute("SELECT patient_name FROM test_results")
            name = cursor.fetchone()[0]
        
        assert name == "田中太郎"

    def test_date_stored(self, storage):
        """Проверка сохранения даты теста."""
        patient = PatientData(name="ДатаТест", age=40, education_years=14)
        result = TestResult(patient=patient, total_time_seconds=35.0, errors_count=0)
        
        before_save = datetime.now()
        storage.save_result(result)
        after_save = datetime.now()
        
        with sqlite3.connect(storage.db_path) as conn:
            cursor = conn.execute("SELECT test_date FROM test_results WHERE patient_name='ДатаТест'")
            date_str = cursor.fetchone()[0]
        
        # Проверяем формат даты
        saved_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        
        # Сравниваем с точностью до секунды (формат БД не включает микросекунды)
        before_save_truncated = before_save.replace(microsecond=0)
        after_save_truncated = after_save.replace(microsecond=0) + timedelta(seconds=1)
        
        assert before_save_truncated <= saved_date <= after_save_truncated

    def test_edge_age_values(self, storage):
        """Проверка граничных значений возраста."""
        # Минимальный возраст
        patient_min = PatientData(name="MinAge", age=1, education_years=0)
        result_min = TestResult(patient=patient_min, total_time_seconds=30.0, errors_count=0)
        storage.save_result(result_min)
        
        # Максимальный возраст
        patient_max = PatientData(name="MaxAge", age=129, education_years=59)
        result_max = TestResult(patient=patient_max, total_time_seconds=30.0, errors_count=0)
        storage.save_result(result_max)
        
        with sqlite3.connect(storage.db_path) as conn:
            cursor = conn.execute("SELECT age FROM test_results ORDER BY id")
            ages = [row[0] for row in cursor.fetchall()]
        
        assert 1 in ages
        assert 129 in ages
