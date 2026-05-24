"""Тесты для валидатора данных пациента."""

import pytest

from nct_app.validators import PatientValidator
from nct_app.models import PatientData
from nct_app.config import MIN_AGE, MAX_AGE, MIN_EDUCATION_YEARS, MAX_EDUCATION_YEARS


class TestPatientValidator:
    """Тесты для PatientValidator."""

    def test_valid_patient(self):
        """Проверка валидных данных пациента."""
        success, patient, error = PatientValidator.validate(
            name="Иванов И.И.",
            age_str="45",
            education_str="16"
        )
        
        assert success is True
        assert patient is not None
        assert patient.name == "Иванов И.И."
        assert patient.age == 45
        assert patient.education_years == 16
        assert error == ""

    def test_empty_name(self):
        """Проверка пустого имени."""
        success, patient, error = PatientValidator.validate(
            name="",
            age_str="30",
            education_str="12"
        )
        
        assert success is False
        assert patient is None
        assert "имя" in error.lower() or "id" in error.lower()

    def test_whitespace_name(self):
        """Проверка имени с пробелами."""
        success, patient, error = PatientValidator.validate(
            name="   ",
            age_str="30",
            education_str="12"
        )
        
        assert success is False
        assert patient is None

    def test_name_with_whitespace_trimmed(self):
        """Проверка обрезки пробелов в имени."""
        success, patient, error = PatientValidator.validate(
            name="  Петров П.П.  ",
            age_str="35",
            education_str="14"
        )
        
        assert success is True
        assert patient is not None
        assert patient.name == "Петров П.П."

    def test_invalid_age_non_integer(self):
        """Проверка невалидного возраста (не число)."""
        success, patient, error = PatientValidator.validate(
            name="Тест",
            age_str="abc",
            education_str="12"
        )
        
        assert success is False
        assert patient is None
        assert "возраст" in error.lower()

    def test_invalid_age_too_low(self):
        """Проверка возраста ниже минимального."""
        success, patient, error = PatientValidator.validate(
            name="Тест",
            age_str="0",
            education_str="12"
        )
        
        assert success is False
        assert patient is None
        assert str(MIN_AGE) in error

    def test_invalid_age_too_high(self):
        """Проверка возраста выше максимального."""
        success, patient, error = PatientValidator.validate(
            name="Тест",
            age_str="130",
            education_str="12"
        )
        
        assert success is False
        assert patient is None
        assert str(MAX_AGE) in error

    def test_valid_age_boundaries(self):
        """Проверка граничных значений возраста."""
        # Минимальный возраст
        success_min, patient_min, _ = PatientValidator.validate(
            name="Тест",
            age_str=str(MIN_AGE),
            education_str="10"
        )
        assert success_min is True
        assert patient_min is not None
        assert patient_min.age == MIN_AGE

        # Максимальный возраст
        success_max, patient_max, _ = PatientValidator.validate(
            name="Тест",
            age_str=str(MAX_AGE),
            education_str="10"
        )
        assert success_max is True
        assert patient_max is not None
        assert patient_max.age == MAX_AGE

    def test_invalid_education_non_integer(self):
        """Проверка невалидных лет обучения (не число)."""
        success, patient, error = PatientValidator.validate(
            name="Тест",
            age_str="30",
            education_str="xyz"
        )
        
        assert success is False
        assert patient is None
        assert "обучения" in error.lower()

    def test_invalid_education_too_low(self):
        """Проверка лет обучения ниже минимального."""
        success, patient, error = PatientValidator.validate(
            name="Тест",
            age_str="30",
            education_str="-1"
        )
        
        assert success is False
        assert patient is None
        assert str(MIN_EDUCATION_YEARS) in error

    def test_invalid_education_too_high(self):
        """Проверка лет обучения выше максимального."""
        success, patient, error = PatientValidator.validate(
            name="Тест",
            age_str="30",
            education_str="60"
        )
        
        assert success is False
        assert patient is None
        assert str(MAX_EDUCATION_YEARS) in error

    def test_valid_education_boundaries(self):
        """Проверка граничных значений лет обучения."""
        # Минимальные годы обучения
        success_min, patient_min, _ = PatientValidator.validate(
            name="Тест",
            age_str="25",
            education_str=str(MIN_EDUCATION_YEARS)
        )
        assert success_min is True
        assert patient_min is not None
        assert patient_min.education_years == MIN_EDUCATION_YEARS

        # Максимальные годы обучения
        success_max, patient_max, _ = PatientValidator.validate(
            name="Тест",
            age_str="80",
            education_str=str(MAX_EDUCATION_YEARS)
        )
        assert success_max is True
        assert patient_max is not None
        assert patient_max.education_years == MAX_EDUCATION_YEARS

    def test_multiple_errors(self):
        """Проверка нескольких ошибок одновременно."""
        success, patient, error = PatientValidator.validate(
            name="",
            age_str="invalid",
            education_str="invalid"
        )
        
        assert success is False
        assert patient is None
        # Должны быть ошибки по всем полям
        assert "имя" in error.lower() or "id" in error.lower()
        assert "возраст" in error.lower()
        assert "обучения" in error.lower()

    def test_float_age(self):
        """Проверка возраста с плавающей точкой."""
        success, patient, error = PatientValidator.validate(
            name="Тест",
            age_str="25.5",
            education_str="12"
        )
        
        assert success is False
        assert patient is None

    def test_negative_age(self):
        """Проверка отрицательного возраста."""
        success, patient, error = PatientValidator.validate(
            name="Тест",
            age_str="-5",
            education_str="12"
        )
        
        assert success is False
        assert patient is None
