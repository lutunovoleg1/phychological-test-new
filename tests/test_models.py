"""Тесты для моделей данных."""

import pytest

from nct_app.models import Circle, PatientData, TestResult


class TestCircle:
    """Тесты для модели Circle."""

    def test_circle_creation(self):
        """Проверка создания круга."""
        circle = Circle(number=5, x=100.0, y=150.0, radius=25.0)
        
        assert circle.number == 5
        assert circle.x == 100.0
        assert circle.y == 150.0
        assert circle.radius == 25.0

    def test_circle_immutable(self):
        """Проверка неизменяемости круга."""
        circle = Circle(number=1, x=0.0, y=0.0, radius=10.0)
        
        with pytest.raises(AttributeError):
            circle.number = 2

    def test_circle_equality(self):
        """Проверка равенства кругов."""
        circle1 = Circle(number=5, x=100.0, y=150.0, radius=25.0)
        circle2 = Circle(number=5, x=100.0, y=150.0, radius=25.0)
        circle3 = Circle(number=6, x=100.0, y=150.0, radius=25.0)
        
        assert circle1 == circle2
        assert circle1 != circle3


class TestPatientData:
    """Тесты для модели PatientData."""

    def test_patient_creation(self):
        """Проверка создания данных пациента."""
        patient = PatientData(name="Иванов И.И.", age=45, education_years=16)
        
        assert patient.name == "Иванов И.И."
        assert patient.age == 45
        assert patient.education_years == 16

    def test_patient_empty_name(self):
        """Проверка создания пациента с пустым именем."""
        patient = PatientData(name="", age=30, education_years=10)
        
        assert patient.name == ""
        assert patient.age == 30

    def test_patient_edge_age(self):
        """Проверка граничных значений возраста."""
        patient_min = PatientData(name="Test", age=1, education_years=0)
        patient_max = PatientData(name="Test", age=129, education_years=0)
        
        assert patient_min.age == 1
        assert patient_max.age == 129


class TestTestResult:
    """Тесты для модели TestResult."""

    def test_result_creation(self):
        """Проверка создания результата теста."""
        patient = PatientData(name="Петров П.П.", age=50, education_years=12)
        result = TestResult(patient=patient, total_time_seconds=45.5, errors_count=2)
        
        assert result.patient.name == "Петров П.П."
        assert result.total_time_seconds == 45.5
        assert result.errors_count == 2

    def test_result_zero_errors(self):
        """Проверка результата без ошибок."""
        patient = PatientData(name="Сидоров С.С.", age=35, education_years=16)
        result = TestResult(patient=patient, total_time_seconds=30.0, errors_count=0)
        
        assert result.errors_count == 0
        assert result.total_time_seconds == 30.0

    def test_result_with_patient_object(self):
        """Проверка связи результата с объектом пациента."""
        patient = PatientData(name="Тест", age=25, education_years=14)
        result = TestResult(patient=patient, total_time_seconds=50.0, errors_count=1)
        
        assert result.patient is patient
        assert result.patient.age == 25
