from __future__ import annotations

import time
from typing import Any, Dict, List

from daonovice.core.plugin_base import DaoPlugin


class InnerBuildingPlugin(DaoPlugin):
    """内建门（技术·阴）：悔恨驱动、六层记忆、自传引擎。"""

    def __init__(self) -> None:
        super().__init__("内建门")
        self.memory_layers: Dict[str, Dict[str, str]] = {
            "精神": {}, "身份": {}, "信念": {}, "能力": {}, "行为": {}, "环境": {},
        }
        self.autobiography: List[Dict[str, Any]] = []

    async def on_activate(self) -> Dict[str, Any]:
        return {"gate": "内建门", "functions": ["悔恨驱动", "市场学习", "六层记忆", "自传引擎"]}

    async def on_command(self, command: str, **kwargs: Any) -> Dict[str, Any]:
        if command == "regret_calculate":
            complexity = kwargs.get("complexity", 0.5)
            error_count = kwargs.get("error_count", 0)
            pain = kwargs.get("pain_relevance", 0.3)
            postponed = kwargs.get("times_postponed", 0)
            score = complexity * 0.3 + error_count * 0.3 + pain * 0.3 + postponed * 0.1
            return {"regret_score": round(score, 2), "trigger": score > 0.7}

        if command == "memory_store":
            layer = kwargs.get("layer", "行为")
            key = kwargs.get("key", "")
            value = kwargs.get("value", "")
            if layer in self.memory_layers:
                self.memory_layers[layer][key] = value
            return {"stored": True, "layer": layer, "key": key}

        if command == "memory_recall":
            layer = kwargs.get("layer", "")
            if layer in self.memory_layers:
                return {"layer": layer, "memories": self.memory_layers[layer]}
            return {"memories": self.memory_layers}

        if command == "autobiography_write":
            chapter = kwargs.get("chapter", f"第{len(self.autobiography) + 1}章")
            content = kwargs.get("content", "")
            self.autobiography.append({"chapter": chapter, "content": content, "time": time.time()})
            return {"written": True, "chapter": chapter, "total": len(self.autobiography)}

        if command == "autobiography_read":
            return {"autobiography": self.autobiography[-5:]}

        return {"error": "未知指令"}
