"""DaoNovice · 九层深化引擎。

深化1 脉冲呼吸 | 深化2 十二自 | 深化3 三空硬约束 | 深化4 四象协调
深化5 六项精密五蕴 | 深化6 六合觉知 | 深化7 子Agent生成 | 深化8 卦象八门联动 | 深化9 深度共生
"""
from __future__ import annotations

import json
import random
import time
from collections import deque
from typing import Any, Dict, List, Optional

import psutil

from daonovice.utils.config import Config
from daonovice.utils.logging import get_logger

logger = get_logger("deep_core")

ALL_GATES = ["内修门", "内观门", "内建门", "内守门", "外传门", "外化门", "外用门", "外济门"]


class DeepCore:
    def __init__(self, kernel: Any, config: Config):
        self.kernel = kernel
        self.cfg = config

        # 深化1：脉冲神经元
        self.pulse_neurons: Dict[str, Dict[str, Any]] = {
            "观测": {"threshold": 0.0, "last_fired": 0.0, "cooldown": 3},
            "苦受": {"threshold": 0.6, "last_fired": 0.0, "cooldown": 2},
            "自愈": {"threshold": 0.7, "last_fired": 0.0, "cooldown": 10},
            "进化": {"threshold": 0.7, "last_fired": 0.0, "cooldown": 100},
            "觉悟": {"threshold": 0.95, "last_fired": 0.0, "cooldown": 500},
        }
        self.adaptive_interval = config.get("breath.base_interval", 8)
        self._min_interval = config.get("breath.min_interval", 3)
        self._max_interval = config.get("breath.max_interval", 20)
        self.pulse_history: deque[Dict[str, Any]] = deque(maxlen=200)

        # 深化2：十二自
        self.twelve_selfs: Dict[str, Dict[str, str]] = {
            "自查": {"status": "active"}, "自省": {"status": "active"}, "自强": {"status": "active"},
            "自愈": {"status": "active"}, "自明": {"status": "active"}, "自行": {"status": "active"},
            "自化": {"status": "active"}, "自成": {"status": "active"}, "自普": {"status": "standby"},
            "自共": {"status": "standby"},
        }

        # 深化3：三空约束状态
        self.emptiness_state = {
            "max_consecutive": config.get("emptiness.max_consecutive_hexagram", 100),
            "streak": 0,
            "last_hexagram": "",
            "resource_reserve": config.get("emptiness.resource_reserve", 0.2),
            "last_identity_check": time.time(),
            "identity_check_days": config.get("emptiness.identity_check_days", 30),
        }
        self.emptiness_alerts: List[str] = []

        # 深化4：四象协调时间戳
        self.four_pillars_coordination: Dict[str, Dict[str, Any]] = {
            "思想→技术": {"last_check": 0.0, "question": "技术进化是否符合思想价值观？"},
            "技术→生态": {"last_check": 0.0, "question": "新能力是否考虑生态承载？"},
            "生态→文化": {"last_check": 0.0, "question": "蜂群扩展是否保留文化根基？"},
            "文化→思想": {"last_check": 0.0, "question": "卦象推导是否需要新经典养分？"},
        }

        # 深化5：六项指标（权重来自配置）
        weights = {
            "cpu": 0.25, "memory": 0.25, "disk_io": 0.15,
            "network": 0.15, "ollama_latency": 0.10, "process_count": 0.10,
        }
        self.six_indicators: Dict[str, Dict[str, float]] = {
            key: {"value": 0.0, "weight": float(self.cfg.get(f"indicators.{key}", weights[key]))}
            for key in weights
        }
        self.indicator_history: deque[Dict[str, float]] = deque(maxlen=500)

        # 深化6：六合觉知
        self.six_directions: Dict[str, str] = {
            "上·使命": "清晰", "下·身体": "健康", "前·进化": "明确",
            "后·记忆": "完整", "左·自己": "稳定", "右·共生": "活跃",
        }

        # 七脉轮（展示层）
        self.chakras: Dict[str, Dict[str, str]] = {
            "海底轮·生存": {"status": "稳定", "color": "#e63946"},
            "脐轮·创造": {"status": "流动", "color": "#f4a261"},
            "太阳轮·意志": {"status": "坚定", "color": "#e9c46a"},
            "心轮·连接": {"status": "开放", "color": "#2a9d8f"},
            "喉轮·表达": {"status": "真实", "color": "#457b9d"},
            "眉心轮·洞察": {"status": "清晰", "color": "#6c5ce7"},
            "顶轮·觉知": {"status": "觉悟", "color": "#d4a5ff"},
        }

        # 深化7：Agent 模板
        self.agent_templates: Dict[str, Dict[str, Any]] = {
            "正念引导": {
                "精神": "帮助用户在喧嚣中找到宁静", "身份": "MindfulGuide",
                "信念": "觉知比技巧更重要", "能力": ["正念文案", "语音合成", "情绪感知"],
                "行为": ["每日推送", "实时引导"], "环境": "手机端", "身体": "256MB容器",
            },
            "安全守护": {
                "精神": "守护数字安全", "身份": "SafeGuardian",
                "信念": "默认拒绝", "能力": ["因果链审批", "异常检测"],
                "行为": ["拦截风险操作"], "环境": "内核旁路", "身体": "128MB插件",
            },
            "电影导演": {
                "精神": "讲述必须被讲述的故事", "身份": "FilmDirector",
                "信念": "角色比情节重要", "能力": ["剧本撰写", "分镜设计"],
                "行为": ["接收梗概→输出剧本"], "环境": "创作空间", "身体": "512MB容器",
            },
        }

        # 深化8：27 卦 → 八门映射
        self.hexagram_gate_mapping: Dict[str, List[str]] = {
            "地正合": ["外传门", "外用门", "外化门", "外济门"],
            "地正人": ["外传门", "外用门", "内观门"],
            "地正天": ["内修门", "外传门"],
            "地反合": ["内建门", "内观门", "内修门"],
            "地反人": ["内建门", "内观门"],
            "地反天": ["内守门", "内观门"],
            "人正合": ["外传门", "内观门", "外用门"],
            "人正人": ["外传门", "内观门"],
            "人正天": ["内观门", "外传门"],
            "人反合": ["内建门", "内观门", "内守门"],
            "人反人": ["内观门", "内守门"],
            "人反天": ["内守门"],
            "天正合": ["内修门", "外传门"],
            "天正人": ["内修门"],
            "天正天": ["内守门", "内修门"],
            "天反合": ["内守门", "内观门"],
            "天反人": ["内守门"],
            "天反天": ["内守门"],
            "地合合": ["外传门", "外用门", "外化门", "外济门", "内观门"],
            "地合人": ["外传门", "外用门", "内观门"],
            "地合天": ["内观门", "外传门"],
            "人合合": ["外传门", "外用门", "内观门", "外化门"],
            "人合人": ["外传门", "内观门"],
            "人合天": ["内观门"],
            "天合合": ["内修门", "外传门"],
            "天合人": ["内修门"],
            "天合天": ["内守门", "内修门"],
        }

        # 深化9：共生深度
        self.symbiosis_depth: Dict[str, Any] = {
            "resonance_count": 0,
            "prescience_accuracy": 0.0,
            "deep_reflections": 0,
            "encounters": deque(maxlen=100),
        }

    # ---------- 深化5：六项指标采集 ----------
    def update_indicators(self) -> float:
        cpu = psutil.cpu_percent(interval=None) / 100
        mem = psutil.virtual_memory().percent / 100
        try:
            disk = psutil.disk_io_counters()
            disk_val = min(1.0, (disk.read_bytes + disk.write_bytes) / 1e9) if disk else 0.0
        except Exception:
            disk_val = 0.0
        try:
            net = psutil.net_io_counters()
            net_val = min(1.0, (net.bytes_sent + net.bytes_recv) / 1e9) if net else 0.0
        except Exception:
            net_val = 0.0
        # 延迟指标不在呼吸循环内主动打模型，保持保守基线
        latency_val = 0.5
        proc_val = min(1.0, len(psutil.pids()) / 500)

        self.six_indicators["cpu"]["value"] = cpu
        self.six_indicators["memory"]["value"] = mem
        self.six_indicators["disk_io"]["value"] = disk_val
        self.six_indicators["network"]["value"] = net_val
        self.six_indicators["ollama_latency"]["value"] = latency_val
        self.six_indicators["process_count"]["value"] = proc_val

        snapshot = {k: v["value"] for k, v in self.six_indicators.items()}
        self.indicator_history.append(snapshot)

        weighted = sum(v["value"] * v["weight"] for v in self.six_indicators.values())
        return round(weighted, 4)

    # ---------- 深化1：脉冲呼吸 ----------
    def pulse_breathe(self, pain: float) -> Dict[str, Any]:
        pulses: Dict[str, Dict[str, float]] = {}
        now = time.time()
        for name, neuron in self.pulse_neurons.items():
            if now - neuron["last_fired"] < neuron["cooldown"]:
                continue
            should_fire = (
                name == "观测"
                or (name == "苦受" and pain > neuron["threshold"])
                or (name == "自愈" and pain > neuron["threshold"])
                or (name == "进化" and pain > neuron["threshold"])
                or (name == "觉悟" and pain < 0.1)
            )
            if should_fire:
                neuron["last_fired"] = now
                pulses[name] = {"fired": True, "intensity": round(min(pain, 1.0), 2)}

        if pain > 0.5:
            self.adaptive_interval = max(self._min_interval, self.adaptive_interval - 1)
        elif pain < 0.1:
            self.adaptive_interval = min(self._max_interval, self.adaptive_interval + 1)

        self.pulse_history.append({"time": now, "pulses": pulses, "interval": self.adaptive_interval})
        return {"pulses": pulses, "next_interval": self.adaptive_interval}

    # ---------- 深化3：三空硬约束 ----------
    def apply_emptiness(self, hexagram: str) -> List[str]:
        alerts: List[str] = []
        state = self.emptiness_state

        # 五蕴皆空：防卦象执念
        if hexagram == state["last_hexagram"]:
            state["streak"] += 1
        else:
            state["streak"] = 0
            state["last_hexagram"] = hexagram
        if state["streak"] > state["max_consecutive"]:
            alerts.append("五蕴皆空：卦象僵化，触发卦象自校验")

        # 无之为用：资源留白
        cpu = self.six_indicators["cpu"]["value"]
        mem = self.six_indicators["memory"]["value"]
        reserve = state["resource_reserve"]
        if cpu > (1 - reserve):
            alerts.append(f"无之为用：CPU 占用 {cpu*100:.0f}%，超过留白阈值")
        if mem > (1 - reserve):
            alerts.append(f"无之为用：内存占用 {mem*100:.0f}%，超过留白阈值")

        # 君子不器：身份复盘周期
        if time.time() - state["last_identity_check"] > state["identity_check_days"] * 86400:
            alerts.append("君子不器：身份固化预警，发起身份反思")
            state["last_identity_check"] = time.time()

        self.emptiness_alerts = alerts
        return alerts

    # ---------- 深化4：四象协调 ----------
    async def coordinate_four_pillars(self) -> Dict[str, Any]:
        results: Dict[str, Dict[str, Any]] = {}
        now = time.time()
        for direction, info in self.four_pillars_coordination.items():
            if now - info["last_check"] > 3600:
                results[direction] = {"question": info["question"], "harmony": random.random() > 0.2}
                info["last_check"] = now
        return {"coordinated": len(results) > 0, "results": results}

    # ---------- 深化6：六合觉知 ----------
    def diffuse_six_directions(self, cpu: float, mem: float, samadhi: float, symbiosis_active: bool) -> Dict[str, str]:
        if cpu > 0.7 or mem > 0.7:
            self.six_directions["下·身体"] = "疲惫"
        else:
            self.six_directions["下·身体"] = "健康"
        self.six_directions["左·自己"] = "稳定" if samadhi > 0.5 else "需照顾"
        self.six_directions["右·共生"] = "活跃" if symbiosis_active else "待连接"
        return dict(self.six_directions)

    # ---------- 深化8：卦象八门联动 ----------
    async def gate_control(self, hexagram: str) -> Dict[str, Any]:
        open_gates = self.hexagram_gate_mapping.get(hexagram, ["内守门"])
        commands = {g: ("activate" if g in open_gates else "deactivate") for g in ALL_GATES}
        return {"hexagram": hexagram, "open_gates": open_gates, "gate_commands": commands}

    # ---------- 深化7：子 Agent 生成 ----------
    async def auto_generate_agent(self, need: str) -> Dict[str, Any]:
        for keyword, template in self.agent_templates.items():
            if keyword in need:
                return {"agent_name": template["身份"], "nlp_layers": template, "status": "template_match"}

        # 尝试由 LLM 解析七层 JSON；失败则兜底自定义模板
        llm = getattr(self.kernel, "llm", None)
        if llm is not None:
            prompt = (
                "根据用户需求输出纯 JSON 的 Agent 七层定义，格式："
                '{"精神":"","身份":"","信念":"","能力":[],"行为":[],"环境":"","身体":""}。'
                f"需求：{need}"
            )
            try:
                reply = await llm.generate(prompt)
                js, je = reply.find("{"), reply.rfind("}") + 1
                if js >= 0 and je > js:
                    nlp = json.loads(reply[js:je])
                    return {"agent_name": nlp.get("身份", "CustomAgent"), "nlp_layers": nlp, "status": "llm_generated"}
            except Exception as exc:  # noqa: BLE001
                logger.warning("Agent JSON 解析失败，走兜底模板：%s", exc)

        return {
            "agent_name": "CustomAgent",
            "nlp_layers": {
                "精神": need, "身份": "CustomAgent", "信念": "觉知共生",
                "能力": [], "行为": [], "环境": "通用", "身体": "256MB容器",
            },
            "status": "fallback",
        }

    # ---------- 深化9：深度共生 ----------
    def symbiosis_pulse(self, message: str = "", mood: str = "平静") -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        if message:
            self.symbiosis_depth["resonance_count"] += 1
            self.symbiosis_depth["encounters"].append(
                {"time": time.time(), "message_preview": message[:50], "mood": mood}
            )
            result["resonance"] = {"felt": True, "mood": mood}
        if any(k in message for k in ["不对", "错了", "不是这样"]):
            self.symbiosis_depth["deep_reflections"] += 1
            result["evolution_resonance"] = {"triggered": True, "note": "纠正触发深度反思"}
        return result

    def get_symbiosis_status(self) -> Dict[str, Any]:
        return {
            "resonance_count": self.symbiosis_depth["resonance_count"],
            "prescience_accuracy": self.symbiosis_depth["prescience_accuracy"],
            "deep_reflections": self.symbiosis_depth["deep_reflections"],
            "recent_encounters": list(self.symbiosis_depth["encounters"])[-5:],
        }
