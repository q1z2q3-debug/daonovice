from __future__ import annotations

from typing import Any, Dict, List

from daonovice.core.plugin_base import DaoPlugin


class OuterExpressionPlugin(DaoPlugin):
    """外传门（思想·阳）：文曲星八步创作管线。"""

    def __init__(self) -> None:
        super().__init__("外传门")
        self.pipeline: List[str] = [
            "素材采集", "AI草稿", "事实核查", "封面生成", "插图编排", "格式化", "人性化", "发布",
        ]

    async def on_activate(self) -> Dict[str, Any]:
        return {"gate": "外传门", "pipeline": self.pipeline}

    async def on_command(self, command: str, **kwargs: Any) -> Dict[str, Any]:
        if command == "write_full":
            topic = kwargs.get("topic", "道")
            style = kwargs.get("style", "散文")
            prompt = f"以{style}风格写一篇关于{topic}的完整文章，800字以内，含标题、导语、正文、结语。"
            reply = await self._core.llm.generate(prompt) if self._core else "文曲入定"
            return {"pipeline_stage": "完成", "title": topic, "content": reply, "stages_completed": self.pipeline}

        if command == "fact_check":
            draft = kwargs.get("draft", "")
            source = kwargs.get("source", "")
            prompt = f"比对草稿与原始素材，标记事实不一致的内容。\n草稿：{draft[:1000]}\n素材：{source[:1000]}"
            reply = await self._core.llm.generate(prompt) if self._core else ""
            return {"check_result": reply[:300]}

        if command == "humanize":
            text = kwargs.get("text", "")
            prompt = f"让以下文字更口语化、更有亲和力，去除机械感：{text[:1000]}"
            reply = await self._core.llm.generate(prompt) if self._core else text
            return {"humanized": reply[:500]}

        if command == "pipeline_status":
            return {"pipeline": self.pipeline}

        return {"error": "未知指令"}
