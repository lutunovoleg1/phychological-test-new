"""Валидация данных пациента."""

from .config import MAX_AGE, MAX_EDUCATION_YEARS, MIN_AGE, MIN_EDUCATION_YEARS
from .models import PatientData


class PatientValidator:
    """Валидатор данных пациента."""

    @staticmethod
    def validate(name: str, age_str: str, education_str: str) -> tuple[bool, PatientData | None, str]:
        """
        Валидация и парсинг данных пациента.

        Returns:
            Кортеж (успех, данные или None, сообщение об ошибке).
        """
        errors = []

        # Проверка имени
        name = name.strip()
        if not name:
            errors.append("Укажите ID или имя пациента.")

        # Парсинг возраста
        try:
            age = int(age_str)
            if not (MIN_AGE <= age <= MAX_AGE):
                errors.append(f"Возраст должен быть от {MIN_AGE} до {MAX_AGE}.")
        except ValueError:
            errors.append("Возраст должен быть целым числом.")
            age = 0

        # Парсинг лет обучения
        try:
            education_years = int(education_str)
            if not (MIN_EDUCATION_YEARS <= education_years <= MAX_EDUCATION_YEARS):
                errors.append(f"Годы обучения должны быть от {MIN_EDUCATION_YEARS} до {MAX_EDUCATION_YEARS}.")
        except ValueError:
            errors.append("Годы обучения должны быть целым числом.")
            education_years = 0

        if errors:
            return False, None, " ".join(errors)

        patient = PatientData(name=name, age=age, education_years=education_years)
        return True, patient, ""
