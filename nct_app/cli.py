"""Точка входа приложения."""

import logging
import sys

try:
    import tkinter as tk
except ModuleNotFoundError:
    tk = None  # type: ignore[assignment]

from .config import DB_PATH
from .ui import ElectronicNctApp


def setup_logging() -> None:
    """Настройка логирования."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(DB_PATH.with_suffix(".log"), encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def main() -> None:
    """Запуск приложения."""
    if tk is None:
        raise SystemExit(
            "Для запуска GUI нужен Python с модулем tkinter/Tcl-Tk. "
            "Переустановите Python с опцией Tcl/Tk или запустите приложение в окружении, где tkinter доступен."
        )

    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Запуск приложения")

    root = tk.Tk()
    app = ElectronicNctApp(root)
    logger.info("GUI инициализирован")
    root.mainloop()
    logger.info("Приложение завершено")


if __name__ == "__main__":
    main()
