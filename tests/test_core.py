"""DaoNovice 基础单元测试：不依赖外部 LLM 与网络。

运行：PYTHONPATH=src pytest -q
"""
from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from daonovice.core.deep_core import DeepCore  # noqa: E402
from daonovice.core.engines_1to9 import (  # noqa: E402
    EightGates, FiveSkandhas, FourPillars, NineGates, OneBody,
    SevenLayers, SixDirections, ThreeEmptiness, TwoWings,
)
from daonovice.memory.regret_store import RegretStore  # noqa: E402
from daonovice.utils.config import Config  # noqa: E402


def _config(tmp: str) -> Config:
    return Config({
        "memory": {"db_path": str(Path(tmp) / "regret.db")},
        "llm": {"doubao": {"enabled": False}},
    })


def test_one_body_breathe():
    body = OneBody()
    result = asyncio.run(body.breathe())
    assert result["alive"] is True
    assert result["breath"] == 1


def test_two_wings():
    wings = TwoWings().get_wings()
    assert wings["principle"] == "自觉觉他"
    assert len(wings["self_benefit"]) == 5
    assert len(wings["altruism"]) == 5


def test_three_emptiness():
    emp = ThreeEmptiness().get_emptiness()
    assert set(emp) == {"buddha", "dao", "confucius"}


def test_four_pillars():
    pillars = FourPillars().get_pillars()
    assert set(pillars) == {"思想", "文化", "技术", "生态"}


def test_five_skandhas_observe():
    sk = FiveSkandhas().observe(cpu=20, mem=30)
    assert sk["受"] == "乐"
    sk2 = FiveSkandhas().observe(cpu=95, mem=95)
    assert sk2["受"] == "苦"


def test_six_directions_introspect():
    result = asyncio.run(SixDirections().introspect({"cpu": 20, "samadhi": 0.8}))
    assert set(result) == {"上", "下", "前", "后", "左", "右"}


def test_seven_layers():
    layers = SevenLayers().get_layers()
    assert list(layers) == ["精神", "身份", "信念", "能力", "行为", "环境", "身体"]


def test_eight_and_nine_gates():
    eight = EightGates().get_gates()
    nine = NineGates().get_all_nine()
    assert len(eight) == 8
    assert len(nine) == 9
    assert "共生门" in nine


def test_regret_store_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        store = RegretStore(str(Path(tmp) / "regret.db"))
        gid = store.add_gap("能力缺口A", 0.82, postponed=2)
        assert store.count_pending(0.7) == 1
        pending = store.fetch_high_score(0.7)
        assert pending[0]["id"] == gid
        store.delete_gap(gid)
        assert store.count_pending(0.7) == 0


def test_deep_core_indicators_and_pulse():
    with tempfile.TemporaryDirectory() as tmp:
        deep = DeepCore(kernel=None, config=_config(tmp))
        pain = deep.update_indicators()
        assert 0.0 <= pain <= 1.0
        pulse = deep.pulse_breathe(pain)
        assert "next_interval" in pulse
        assert deep._min_interval <= deep.adaptive_interval <= deep._max_interval


def test_gate_control_mapping():
    with tempfile.TemporaryDirectory() as tmp:
        deep = DeepCore(kernel=None, config=_config(tmp))
        result = asyncio.run(deep.gate_control("地正合"))
        assert "外传门" in result["open_gates"]
        assert result["gate_commands"]["外传门"] == "activate"
        assert result["gate_commands"]["内守门"] == "deactivate"


def test_agent_template_match_and_fallback():
    with tempfile.TemporaryDirectory() as tmp:
        deep = DeepCore(kernel=None, config=_config(tmp))
        matched = asyncio.run(deep.auto_generate_agent("我需要一个正念引导师"))
        assert matched["status"] == "template_match"
        fallback = asyncio.run(deep.auto_generate_agent("未知领域的定制助手XYZ"))
        assert fallback["status"] == "fallback"
        assert "精神" in fallback["nlp_layers"]


def test_emptiness_alerts_on_resource_pressure():
    with tempfile.TemporaryDirectory() as tmp:
        deep = DeepCore(kernel=None, config=_config(tmp))
        deep.six_indicators["cpu"]["value"] = 0.95
        alerts = deep.apply_emptiness("地正合")
        assert any("CPU" in a for a in alerts)
