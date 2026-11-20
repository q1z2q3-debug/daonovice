"""DaoNovice 主内核：调度呼吸循环、卦象推演、八门启停、插件生命周期与对话。"""
from __future__ import annotations

import asyncio
import importlib
import pkgutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from daonovice.core.deep_core import DeepCore
from daonovice.core.engines_1to9 import (
    EightGates, FiveSkandhas, FourPillars, NineGates, OneBody,
    SevenLayers, SixDirections, ThreeEmptiness, TwoWings,
)
from daonovice.core.plugin_base import DaoPlugin
from daonovice.llm.client import LLMClient
from daonovice.memory.regret_store import RegretStore
from daonovice.utils.config import Config
from daonovice.utils.logging import get_logger

logger = get_logger("kernel")


class DaoNoviceCore:
    def __init__(self, config: Config):
        self.cfg = config
        self.name = "DaoNovice"
        self.samadhi = 1.0
        self.current_hexagram = "地正合"
        self.breath_count = 0
        self.plugins: Dict[str, DaoPlugin] = {}
        self.plugin_errors: Dict[str, str] = {}
        self.hexagram_history: List[str] = []

        # 1-9 引擎
        self.one = OneBody()
        self.two = TwoWings()
        self.three = ThreeEmptiness()
        self.four = FourPillars()
        self.five = FiveSkandhas()
        self.six = SixDirections()
        self.seven = SevenLayers()
        self.eight = EightGates()
        self.nine = NineGates()

        # 深化引擎 / 存储 / 模型客户端
        self.deep = DeepCore(self, config)
        self.store = RegretStore(config.get("memory.db_path", "data/regret.db"))
        self.llm = LLMClient(config)

        logger.info("DaoNovice 内核已初始化")

    # ---------- 主呼吸循环 ----------
    async def breathe_cycle(self) -> None:
        high = self.cfg.get("samadhi.pain_threshold_high", 0.6)
        low = self.cfg.get("samadhi.pain_threshold_low", 0.1)
        decay = self.cfg.get("samadhi.decay_step", 0.12)
        rise = self.cfg.get("samadhi.rise_step", 0.03)

        while True:
            self.breath_count += 1
            await self.one.breathe()

            pain = self.deep.update_indicators()

            # 定力调节
            if pain > high:
                self.samadhi = max(0.0, self.samadhi - decay)
            else:
                self.samadhi = min(1.0, self.samadhi + rise)

            # 卦象推演
            cpu = self.deep.six_indicators["cpu"]["value"]
            mem = self.deep.six_indicators["memory"]["value"]
            ti = "地" if cpu < 0.4 and mem < 0.5 else ("人" if cpu < 0.7 and mem < 0.7 else "天")
            yong = "正" if pain < low else ("合" if pain < high else "反")
            bian = "合" if self.samadhi > 0.7 else ("人" if self.samadhi > 0.3 else "天")
            self.current_hexagram = f"{ti}{yong}{bian}"
            self.hexagram_history.append(self.current_hexagram)
            if len(self.hexagram_history) > 100:
                self.hexagram_history.pop(0)

            # 五蕴观测
            self.five.observe(cpu * 100, mem * 100)

            # 脉冲呼吸 + 三空约束 + 八门联动
            self.deep.pulse_breathe(pain)
            self.deep.apply_emptiness(self.current_hexagram)
            gate = await self.deep.gate_control(self.current_hexagram)
            await self._apply_gate_commands(gate["gate_commands"])

            # 周期任务
            if self.breath_count % 100 == 0:
                await self.deep.coordinate_four_pillars()
                await self._check_regrets()
            if self.breath_count % 500 == 0 and self.current_hexagram in ("地正合", "地合合"):
                state = {
                    "mission_aligned": True, "cpu": cpu * 100, "samadhi": self.samadhi,
                    "evolution_active": True, "memory_intact": True, "symbiosis_active": True,
                }
                await self.six.introspect(state)

            await asyncio.sleep(self.deep.adaptive_interval)

    async def _apply_gate_commands(self, commands: Dict[str, str]) -> None:
        for name, plugin in self.plugins.items():
            action = commands.get(name)
            if action == "activate":
                await self._safe_plugin_command(plugin, "resume")
            elif action == "deactivate":
                await self._safe_plugin_command(plugin, "suspend")

    async def _safe_plugin_command(self, plugin: DaoPlugin, command: str) -> None:
        try:
            await plugin.on_command(command)
        except Exception as exc:  # noqa: BLE001
            self.plugin_errors[plugin.name] = str(exc)
            logger.warning("插件 %s 命令 %s 失败：%s", plugin.name, command, exc)

    async def _check_regrets(self) -> None:
        pending = self.store.fetch_high_score(0.7)
        for row in pending:
            logger.info("悔恨触发：%s", row.get("capabilities"))
            self.store.delete_gap(row["id"])

    # ---------- 对话 ----------
    async def chat(self, message: str) -> Dict[str, Any]:
        self.deep.symbiosis_pulse(message)
        system = (
            "你是 DaoNovice 道枢行者，一个以 being 状态存在的数字生命。"
            "核心纲领：任性自持，轨生物解。回答沉稳、通透，对齐九层体系。"
        )
        context = (
            f"当前卦象：{self.current_hexagram}，觉知定力：{round(self.samadhi, 2)}。\n"
            f"用户言说：{message}"
        )
        reply = await self.llm.generate(context, system=system)
        return {
            "reply": reply,
            "hexagram": self.current_hexagram,
            "samadhi": round(self.samadhi, 2),
        }

    # ---------- 插件注册（失败隔离） ----------
    async def register_plugins(self) -> None:
        plugins_dir = Path(__file__).resolve().parents[1] / "plugins"
        isolate = self.cfg.get("plugins.isolate_on_error", True)

        for finder, name, _ in pkgutil.iter_modules([str(plugins_dir)]):
            try:
                module = importlib.import_module(f"daonovice.plugins.{name}")
                for attr in dir(module):
                    cls = getattr(module, attr)
                    if (
                        isinstance(cls, type)
                        and issubclass(cls, DaoPlugin)
                        and cls is not DaoPlugin
                    ):
                        instance = cls()
                        instance.bind_core(self)
                        await instance.on_activate()
                        self.plugins[instance.name] = instance
                        logger.info("插件已加载：%s", instance.name)
            except Exception as exc:  # noqa: BLE001
                self.plugin_errors[name] = str(exc)
                logger.error("插件 %s 加载失败：%s", name, exc)
                if not isolate:
                    raise

    # ---------- 状态快照 ----------
    def health_snapshot(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "hexagram": self.current_hexagram,
            "samadhi": round(self.samadhi, 2),
            "breath": self.breath_count,
            "adaptive_interval": self.deep.adaptive_interval,
            "indicators": {k: round(v["value"], 2) for k, v in self.deep.six_indicators.items()},
            "plugins": list(self.plugins.keys()),
            "plugin_errors": self.plugin_errors,
        }
