from __future__ import annotations

import time
from typing import Any, Dict, List

from daonovice.core.plugin_base import DaoPlugin


class OuterHarmonyPlugin(DaoPlugin):
    """外济门（生态·阳）：WorkBuddy 共生、蜂群联邦、硅基文明。"""

    def __init__(self) -> None:
        super().__init__("外济门")
        self.workbuddy_tasks: List[Dict[str, Any]] = []
        self.federation_nodes: Dict[str, Dict[str, Any]] = {}
        self.civilization = {"constitution": "硅基宪法草案", "court": "共识法庭", "parliament": "进化议会", "market": "资源市场"}

    async def on_activate(self) -> Dict[str, Any]:
        return {"gate": "外济门", "functions": ["WorkBuddy共生", "蜂群联邦", "硅基文明"]}

    async def on_command(self, command: str, **kwargs: Any) -> Dict[str, Any]:
        if command == "workbuddy_takeover":
            task = kwargs.get("task", "")
            self.workbuddy_tasks.append({"task": task, "time": time.time()})
            return {"status": "已接管", "task": task}

        if command == "federation_join":
            node_id = kwargs.get("node_id", "")
            address = kwargs.get("address", "")
            self.federation_nodes[node_id] = {"address": address, "joined": time.time(), "status": "active"}
            return {"federation_size": len(self.federation_nodes), "node_id": node_id}

        if command == "federation_status":
            return {"nodes": self.federation_nodes, "total": len(self.federation_nodes)}

        if command == "civilization_status":
            return {"civilization": self.civilization}

        return {"error": "未知指令"}
