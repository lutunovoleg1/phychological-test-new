"""Модели данных."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Circle:
    """Представление круга с числом на холсте."""

    number: int
    x: float
    y: float
    radius: float


@dataclass
class PatientData:
    """Данные пациента для теста."""

    name: str
    age: int
    education_years: int


@dataclass
class TestResult:
    """Результат прохождения теста."""

    patient: PatientData
    total_time_seconds: float
    errors_count: int
    test_date: datetime | None = None
