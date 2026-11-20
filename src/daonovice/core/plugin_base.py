"""插件统一基类：所有八门 / 共生门插件继承此接口。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class DaoPlugin(ABC):
    def __init__(self, name: str):
        self.name = name
        self._core: Optional[Any] = None

    def bind_core(self, core: Any) -> None:
        """绑定主内核，插件可读取内核状态、调用内核能力。"""
        self._core = core

    @abstractmethod
    async def on_activate(self) -> Dict[str, Any]:
        """插件激活钩子，返回激活信息。"""

    @abstractmethod
    async def on_command(self, command: str, **kwargs: Any) -> Dict[str, Any]:
        """插件命令入口。"""

    def get_info(self) -> Dict[str, str]:
        return {"name": self.name, "status": "active"}
