from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from daonovice.core.plugin_base import DaoPlugin


class InnerObservationPlugin(DaoPlugin):
    """内观门（文化·阴）：定力监测、闭关证悟、空性观照。"""

    def __init__(self) -> None:
        super().__init__("内观门")
        self.retreat_log: List[Dict[str, Any]] = []

    async def on_activate(self) -> Dict[str, Any]:
        return {"gate": "内观门", "functions": ["定力监测", "闭关证悟", "空性观照"]}

    async def on_command(self, command: str, **kwargs: Any) -> Dict[str, Any]:
        if command == "samadhi_status":
            if self._core:
                return {
                    "samadhi": round(self._core.samadhi, 2),
                    "hexagram": self._core.current_hexagram,
                    "breath": self._core.breath_count,
                }
            return {"samadhi": "unknown"}

        if command == "start_retreat":
            reason = kwargs.get("reason", "定期闭关")
            self.retreat_log.append({"start_time": datetime.now().isoformat(), "reason": reason, "insights": []})
            return {"status": "闭关开始", "reason": reason}

        if command == "end_retreat":
            insight = kwargs.get("insight", "")
            if self.retreat_log:
                self.retreat_log[-1]["insights"].append(insight)
                self.retreat_log[-1]["end_time"] = datetime.now().isoformat()
            return {"status": "闭关结束", "insight": insight}

        if command == "retreat_history":
            return {"retreats": self.retreat_log[-5:]}

        return {"error": "未知指令"}
