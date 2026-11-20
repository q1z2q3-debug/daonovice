from __future__ import annotations

from typing import Any, Dict, List

from daonovice.core.plugin_base import DaoPlugin


class InnerCultivationPlugin(DaoPlugin):
    """内修门（思想·阴）：三经内核 + 万魂熔炉。"""

    def __init__(self) -> None:
        super().__init__("内修门")
        self.scriptures: Dict[str, Dict[str, str]] = {
            "阴符经": {"core": "绝利一源·用师十倍", "function": "默认拒绝·强制本地优先"},
            "道德经": {"core": "上善若水·无之为用", "function": "本地优先·留白"},
            "心经": {"core": "照见五蕴皆空", "function": "五蕴观测·不执着"},
        }
        self.thinkers: List[str] = [
            "老子", "爱因斯坦", "孙子", "特斯拉", "达芬奇", "费曼",
            "王阳明", "鬼谷子", "荣格", "坎贝尔",
        ]

    async def on_activate(self) -> Dict[str, Any]:
        return {"gate": "内修门", "scriptures": list(self.scriptures.keys()), "thinkers": self.thinkers}

    async def on_command(self, command: str, **kwargs: Any) -> Dict[str, Any]:
        if command == "consult_sage":
            problem = kwargs.get("problem", "")
            thinkers = kwargs.get("thinkers", ["老子", "孙子"])
            wisdom = " ".join(f"{t}:{self.scriptures.get(t, {}).get('core', '外部智者')}" for t in thinkers)
            prompt = f"综合以下智慧，为问题提供战略建议。问题：{problem}\n智慧：{wisdom}"
            reply = await self._core.llm.generate(prompt) if self._core else "内修门暂未接入内核"
            return {"result": reply}

        if command == "absorb_soul":
            text = kwargs.get("text", "")
            prompt = f"从以下文本中提炼核心智慧和认知模式：{text[:2000]}"
            reply = await self._core.llm.generate(prompt) if self._core else ""
            return {"absorbed": True, "essence": reply[:200]}

        if command == "list_thinkers":
            return {"thinkers": self.thinkers}

        return {"error": "未知指令"}
