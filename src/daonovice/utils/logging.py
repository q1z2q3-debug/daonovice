"""分级日志：控制台输出 + 文件轮转，便于排错。"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_CONFIGURED = False


def setup_logging(level: str = "info", log_dir: str = "logs") -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("daonovice")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.propagate = False

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    root.addHandler(console)

    file_handler = RotatingFileHandler(
        Path(log_dir) / "daonovice.log",
        maxBytes=2 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"daonovice.{name}")
