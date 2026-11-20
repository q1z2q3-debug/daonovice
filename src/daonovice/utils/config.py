"""配置加载：读取 YAML，环境变量覆盖敏感项。"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml

DEFAULT_CONFIG = Path(__file__).resolve().parents[3] / "config" / "config.yaml"


class Config:
    """嵌套字典的轻量封装，支持点路径取值。"""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Config":
        cfg_path = Path(path) if path else DEFAULT_CONFIG
        if cfg_path.exists():
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}
        # 环境变量覆盖：豆包密钥不入库
        doubao = data.setdefault("llm", {}).setdefault("doubao", {})
        doubao["api_key"] = os.getenv("ARK_API_KEY", doubao.get("api_key", ""))
        return cls(data)

    def get(self, dotted: str, default: Any = None) -> Any:
        node: Any = self._data
        for part in dotted.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default
        return node

    @property
    def raw(self) -> Dict[str, Any]:
        return self._data
