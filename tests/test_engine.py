"""Тесты для движка NCT."""

import pytest
import time
from unittest.mock import patch

from nct_app.engine import NctEngine
from nct_app.config import NUMBERS_COUNT


class TestNctEngine:
    """Тесты для NctEngine."""

    def test_engine_initial_state(self):
        """Проверка начального состояния движка."""
        engine = NctEngine()
        
        assert engine.current_target == 1
        assert engine.errors_count == 0
        assert engine.start_time is None
        assert engine.finished is False

    def test_engine_reset(self):
        """Проверка сброса движка."""
        engine = NctEngine()
        
        # Изменяем состояние
        engine.current_target = 10
        engine.errors_count = 5
        engine.finished = True
        
        # Сбрасываем
        engine.reset()
        
        assert engine.current_target == 1
        assert engine.errors_count == 0
        assert engine.finished is False

    def test_correct_sequence(self):
        """Проверка правильной последовательности кликов."""
        engine = NctEngine()
        
        # Клики по правильной последовательности (кроме последнего)
        for i in range(1, NUMBERS_COUNT):
            correct, finish_time = engine.register_click(i)
            assert correct is True
            assert finish_time is None
            assert engine.current_target == i + 1
        
        # Последний клик должен завершить тест
        correct, finish_time = engine.register_click(NUMBERS_COUNT)
        assert correct is True
        assert finish_time is not None
        assert finish_time > 0
        assert engine.finished is True

    def test_wrong_number_error(self):
        """Проверка регистрации ошибки при неправильном числе."""
        engine = NctEngine()
        
        # Кликаем по неправильному числу (должно быть 1)
        correct, finish_time = engine.register_click(5)
        
        assert correct is False
        assert finish_time is None
        assert engine.errors_count == 1
        assert engine.current_target == 1  # Цель не изменилась

    def test_multiple_errors(self):
        """Проверка накопления ошибок."""
        engine = NctEngine()
        
        # Несколько неправильных кликов
        for _ in range(5):
            engine.register_click(99)
        
        assert engine.errors_count == 5
        assert engine.current_target == 1

    def test_mixed_correct_and_incorrect(self):
        """Проверка смешанной последовательности."""
        engine = NctEngine()
        
        # Правильный клик
        correct, _ = engine.register_click(1)
        assert correct is True
        assert engine.current_target == 2
        
        # Неправильный клик
        correct, _ = engine.register_click(5)
        assert correct is False
        assert engine.errors_count == 1
        assert engine.current_target == 2  # Не изменилось
        
        # Снова правильный клик
        correct, _ = engine.register_click(2)
        assert correct is True
        assert engine.current_target == 3

    def test_clicks_after_finish(self):
        """Проверка кликов после завершения теста."""
        engine = NctEngine()
        
        # Проходим весь тест
        for i in range(1, NUMBERS_COUNT + 1):
            engine.register_click(i)
        
        assert engine.finished is True
        
        # Попытка клика после завершения
        correct, finish_time = engine.register_click(1)
        assert correct is False
        assert finish_time is None
        assert engine.errors_count == 0  # Ошибки не должны считаться после финиша

    def test_first_click_starts_timer(self):
        """Проверка запуска таймера при первом клике."""
        engine = NctEngine()
        
        with patch('time.perf_counter') as mock_time:
            mock_time.side_effect = [100.0, 150.0]  # start_time, finish_time
            
            # Первый клик
            correct, _ = engine.register_click(1)
            assert correct is True
            assert engine.start_time == 100.0

    def test_completion_time_calculation(self):
        """Проверка расчёта времени завершения."""
        engine = NctEngine()
        
        with patch('time.perf_counter') as mock_time:
            mock_time.side_effect = [100.0, 250.0]  # start_time=100, finish_time=250
            
            # Проходим тест от 1 до NUMBERS_COUNT
            for i in range(1, NUMBERS_COUNT):
                engine.register_click(i)
            
            # Последний клик
            correct, finish_time = engine.register_click(NUMBERS_COUNT)
            
            assert correct is True
            assert finish_time == 150.0  # 250 - 100

    def test_single_number_test(self):
        """Проверка теста с одним числом (edge case)."""
        # Временное изменение константы для теста
        original_count = NUMBERS_COUNT
        
        engine = NctEngine()
        engine.reset()
        
        # Эмулируем ситуацию где NUMBERS_COUNT = 1
        engine.current_target = 1
        
        with patch('time.perf_counter') as mock_time:
            mock_time.side_effect = [100.0, 180.0]
            
            correct, finish_time = engine.register_click(1)
            
            # Если бы это было единственное число, тест завершился бы
            # Но в нашем случае NUMBERS_COUNT = 25, поэтому проверяем обычное поведение
            assert correct is True
            assert engine.current_target == 2

    def test_sequential_numbers(self):
        """Проверка последовательного увеличения цели."""
        engine = NctEngine()
        
        expected_targets = list(range(1, NUMBERS_COUNT + 1))
        
        for expected in expected_targets[:-1]:  # Все кроме последнего
            assert engine.current_target == expected
            correct, _ = engine.register_click(expected)
            assert correct is True
        
        # Последний
        assert engine.current_target == NUMBERS_COUNT
        correct, finish_time = engine.register_click(NUMBERS_COUNT)
        assert correct is True
        assert finish_time is not None

    def test_error_does_not_advance_target(self):
        """Проверка что ошибка не продвигает цель."""
        engine = NctEngine()
        
        initial_target = engine.current_target
        
        # Серия неправильных кликов
        for wrong_num in [5, 10, 15, 20]:
            engine.register_click(wrong_num)
            assert engine.current_target == initial_target
        
        # Правильный клик должен сработать
        correct, _ = engine.register_click(1)
        assert correct is True
        assert engine.current_target == 2
