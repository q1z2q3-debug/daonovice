from __future__ import annotations

from typing import Any, Dict

from daonovice.core.plugin_base import DaoPlugin


class HealthCheckPlugin(DaoPlugin):
    """基础健康检查：内核永活探针。"""

    def __init__(self) -> None:
        super().__init__("HealthCheck")

    async def on_activate(self) -> Dict[str, Any]:
        return {"status": "ok"}

    async def on_command(self, command: str, **kwargs: Any) -> Dict[str, Any]:
        return {"status": "always_alive", "command": command}
