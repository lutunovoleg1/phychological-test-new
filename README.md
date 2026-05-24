# eNCT-A — Электронный тест NCT-A (Number Connection Test)

Приложение для проведения электронного варианта психологического теста NCT-A с использованием GUI на Tkinter и хранения данных в SQLite.

📄 **Научная основа:** [Исследование eNCT-A](https://pubmed.ncbi.nlm.nih.gov/28092641/)

---

## 📋 Описание

### Механика
В отличие от классического NCT-A, где соединяют цифры линиями, в eNCT-A пользователь последовательно кликает/тапает по кругам с цифрами от 1 до 25. При правильном нажатии круг меняет цвет.

### Валидация и точность
Исследования подтвердили 100% корреляцию eNCT-A с бумажной версией (PHES-батарея). Приложение:
- Автоматически корректирует результат по возрасту
- Блокирует ошибочные клики без остановки таймера
- Фиксирует время выполнения и ошибки

### Алгоритм генерации поля
Каждый тест генерирует уникальное расположение цифр:
- **Сетка 5×5** — экран делится на ячейки, в каждой — одна цифра
- **Рандомизация** — числа от 1 до 25 перемешиваются
- **Безопасные отступы** — случайное смещение внутри ячейки без выхода за границы
- **Масштабируемость** — координаты в % от размера окна (работает на любых экранах)

---

## 🏗️ Архитектура проекта

```
phychological-test-new/
├── main.py              # Точка входа
├── nct_app/             # Основной пакет приложения
│   ├── __init__.py
│   ├── cli.py           # CLI-интерфейс (опционально)
│   ├── config.py        # Константы и настройки
│   ├── engine.py        # Бизнес-логика теста
│   ├── layout.py        # Генерация расположения кругов
│   ├── models.py        # Модели данных (Circle, PatientData, TestResult)
│   ├── storage.py       # Работа с SQLite
│   ├── ui.py            # GUI на Tkinter
│   └── validators.py    # Валидация входных данных
├── tests/               # Юнит-тесты (pytest)
│   ├── test_models.py
│   ├── test_validators.py
│   ├── test_engine.py
│   └── test_storage.py
├── pyproject.toml       # Конфигурация проекта
└── README.md
```

### Ключевые компоненты
- **models.py** — неизменяемые dataclass для данных пациента и результатов
- **validators.py** — строгая валидация возраста, ID, лет обучения
- **engine.py** — управление состоянием теста, таймером, обработкой кликов
- **layout.py** — алгоритм генерации поля без перекрытий
- **storage.py** — сохранение/загрузка из SQLite с автосозданием схемы
- **ui.py** — интерфейс на Tkinter, отделён от бизнес-логики
- **config.py** — центральное хранилище констант

---

## 🚀 Установка и запуск

### Требования
- Python 3.10+
- Tkinter (встроен в стандартную сборку Python)
- SQLite (встроен в Python)

**Проверка Tkinter:**
```bash
python -c "import tkinter; print('Tkinter доступен')"
```

Если ошибка — переустановите Python с опцией **Tcl/Tk**.

### Быстрый старт (для разработки)

```bash
git clone https://github.com/lutunovoleg1/phychological-test-new.git
cd phychological-test-new

# Создание виртуального окружения (рекомендуется)
python -m venv .venv

# Активация
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Установка зависимостей (если будут добавлены)
pip install -e .

# Запуск
python main.py
```

### Запуск без виртуального окружения
```bash
python main.py
```

---

## ✅ Тестирование

Проект покрыт юнит-тестами (48 тестов):

```bash
# Установка pytest (если не установлен)
pip install pytest

# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=nct_app

# Запуск отдельного модуля
pytest tests/test_validators.py -v
```

**Покрытие:**
- Модели данных — создание, неизменяемость, сравнение
- Валидаторы — граничные значения, множественные ошибки
- Движок — логика кликов, тайминг, состояния
- Хранилище — CRUD-операции, персистентность, Unicode

---

## 💾 Хранение данных

Все результаты сохраняются в локальный SQLite-файл `nct_results.db` (создаётся автоматически в корне проекта).

**Структура БД:**
- `id` — первичный ключ
- `patient_id`, `name`, `age`, `education_years` — данные пациента
- `total_time_ms` — время выполнения (мс)
- `errors_count` — количество ошибок
- `timestamp` — дата и время теста

---

## 📦 Сборка релиза (Windows / Linux)

Для распространения приложения без необходимости установки Python используйте **PyInstaller**.

### 1. Подготовка

```bash
pip install pyinstaller
```

### 2. Сборка для Windows (.exe)

На Windows выполните:

```bash
pyinstaller --onefile --windowed --name "eNCT-A" --icon=icon.ico main.py
```

**Параметры:**
- `--onefile` — один исполняемый файл
- `--windowed` — без консольного окна
- `--name` — имя приложения
- `--icon` — иконка (опционально, создайте `icon.ico`)

**Результат:** `dist/eNCT-A.exe`

### 3. Сборка для Linux (.AppImage или бинарник)

На Linux:

```bash
# Вариант 1: Один бинарный файл
pyinstaller --onefile --windowed --name "eNCT-A" main.py

# Вариант 2: AppImage (требует additional tools)
# Установите appimagetool и создайте AppDir структуру
```

**Результат:** `dist/eNCT-A`

**Важно для Linux:**
- Убедитесь, что Tkinter установлен: `sudo apt-get install python3-tk`
- Для распространения среди пользователей без Python рассмотрите Docker или статическую сборку

### 4. Кроссплатформенная сборка

Для сборки под обе платформы используйте CI/CD (GitHub Actions):

```yaml
# .github/workflows/build.yml
name: Build Release

on: [push]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: { python-version: '3.10' }
      - run: pip install pyinstaller
      - run: pyinstaller --onefile --windowed --name "eNCT-A" main.py
      - uses: actions/upload-artifact@v3
        with: { name: eNCT-A-windows, path: dist/eNCT-A.exe }

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: { python-version: '3.10' }
      - run: sudo apt-get install python3-tk
      - run: pip install pyinstaller
      - run: pyinstaller --onefile --windowed --name "eNCT-A" main.py
      - uses: actions/upload-artifact@v3
        with: { name: eNCT-A-linux, path: dist/eNCT-A }
```

### 5. Публикация релиза

1. Создайте тег: `git tag v1.0.0 && git push origin v1.0.0`
2. На GitHub перейдите в **Releases → Draft a new release**
3. Загрузите артефакты из CI/CD или локальной сборки
4. Добавьте описание изменений (CHANGELOG)

---

## 🛠️ Разработка

### Структура модулей

| Модуль | Ответственность |
|--------|----------------|
| `models.py` | Dataclass: Circle, PatientData, TestResult |
| `validators.py` | Валидация ввода (возраст 18-99, ID, образование) |
| `engine.py` | Состояние теста, обработка кликов, таймер |
| `layout.py` | Генерация поля 5×5 без перекрытий |
| `storage.py` | SQLite CRUD операции |
| `ui.py` | Tkinter GUI, привязка к engine |
| `config.py` | Константы (размеры, цвета, таймауты) |

### Добавление функциональности

1. Новые правила валидации → `validators.py` + тесты
2. Изменение логики теста → `engine.py` + тесты
3. Новый формат хранения → `storage.py` + миграции
4. Изменение UI → `ui.py` (не затрагивая engine)

---

## 📝 Лицензия

Проект создан для исследовательских целей. При использовании в публикациях ссылайтесь на [оригинальное исследование](https://pubmed.ncbi.nlm.nih.gov/28092641/).

---

## 🤝 Вклад

1. Fork репозитория
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

**Требования к PR:**
- Все тесты проходят (`pytest`)
- Код отформатирован (`black`, `isort`)
- Добавлены тесты для новой функциональности
