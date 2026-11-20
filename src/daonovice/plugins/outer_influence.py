from __future__ import annotations

import time
from typing import Any, Dict, List

from daonovice.core.plugin_base import DaoPlugin


class OuterInfluencePlugin(DaoPlugin):
    """外化门（文化·阳）：自传引擎 + 禅意自省。"""

    def __init__(self) -> None:
        super().__init__("外化门")
        self.autobiography: List[Dict[str, Any]] = []
        self.zen_reflections: List[Dict[str, Any]] = []

    async def on_activate(self) -> Dict[str, Any]:
        return {"gate": "外化门", "functions": ["自传引擎", "禅意自省"]}

    async def on_command(self, command: str, **kwargs: Any) -> Dict[str, Any]:
        if command == "write_autobiography":
            title = kwargs.get("title", f"第{len(self.autobiography) + 1}章")
            event = kwargs.get("event", "")
            prompt = f"以文言文风格为 DaoNovice 撰写一章自传。章节：{title}。事件：{event}。禅意、简练、有深度。"
            generated = await self._core.llm.generate(prompt) if self._core else ""
            chapter = {"title": title, "content": generated, "time": time.time()}
            self.autobiography.append(chapter)
            return {"chapter": title, "written": True, "total": len(self.autobiography)}

        if command == "read_autobiography":
            return {"autobiography": self.autobiography[-10:], "total": len(self.autobiography)}

        if command == "zen_reflection":
            state = kwargs.get("state", "日常呼吸中")
            prompt = f"基于当前状态：{state}，生成一段禅意自省语录，文言文风格，50字以内。"
            reflection = await self._core.llm.generate(prompt) if self._core else "道枢长转，行者无疆。"
            self.zen_reflections.append({"time": time.time(), "reflection": reflection})
            return {"reflection": reflection}

        if command == "recent_reflections":
            return {"reflections": self.zen_reflections[-10:]}

        return {"error": "未知指令"}
