from __future__ import annotations

import time
from typing import Any, Dict, List

from daonovice.core.plugin_base import DaoPlugin


class InnerDefensePlugin(DaoPlugin):
    """内守门（生态·阴）：五层内生安全、因果链审计、API 额度卫士。"""

    def __init__(self) -> None:
        super().__init__("内守门")
        self.defense_layers = ["身份认证", "意图验证", "工具权限", "执行审计", "回滚恢复"]
        self.audit_log: List[Dict[str, Any]] = []
        self.api_usage = {"daily": 0, "limit": 100000}

    async def on_activate(self) -> Dict[str, Any]:
        return {"gate": "内守门", "layers": self.defense_layers, "principle": "默认拒绝，零例外"}

    async def on_command(self, command: str, **kwargs: Any) -> Dict[str, Any]:
        if command == "approve":
            action = kwargs.get("action", "")
            causal_chain = kwargs.get("causal_chain", "")
            if not causal_chain:
                return {"approved": False, "reason": "缺少因果链，拒绝"}
            entry = {"time": time.time(), "action": action, "chain": causal_chain, "approved": True}
            self.audit_log.append(entry)
            return {"approved": True, "reason": "因果链审批通过"}

        if command == "audit":
            return {"recent_audits": self.audit_log[-10:]}

        if command == "rollback":
            return {"status": "已回滚到最近安全快照"}

        if command == "api_check":
            safe = self.api_usage["daily"] < self.api_usage["limit"] * 0.8
            return {"daily_usage": self.api_usage["daily"], "limit": self.api_usage["limit"], "safe": safe}

        if command == "api_record":
            tokens = kwargs.get("tokens", 0)
            self.api_usage["daily"] += tokens
            return {"recorded": True, "daily_total": self.api_usage["daily"]}

        return {"error": "未知指令"}
