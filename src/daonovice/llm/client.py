"""双底座大模型客户端：本地 Ollama 优先，豆包方舟可选兜底。

能力：
- 熔断器：连续失败达到阈值后进入冷却，冷却期内不再打远端，直接降级；
- 重试：单次底座失败后有限重试；
- 降级：全部底座不可用时返回固定禅意文案，不阻塞主呼吸循环；
- 密钥：豆包 api_key 从环境变量 ARK_API_KEY 读取，不入库。
"""
from __future__ import annotations

import asyncio
import time
from typing import Optional

import httpx

from daonovice.utils.config import Config
from daonovice.utils.logging import get_logger

logger = get_logger("llm")

FALLBACK_REPLY = "道枢无言，算力底座暂不可达，内核仍在呼吸。"


class CircuitBreaker:
    def __init__(self, failure_threshold: int, cooldown_seconds: int):
        self.failure_threshold = failure_threshold
        self.cooldown = cooldown_seconds
        self._failures = 0
        self._open_until = 0.0

    def allow(self) -> bool:
        if self._failures < self.failure_threshold:
            return True
        return time.time() >= self._open_until

    def record_success(self) -> None:
        self._failures = 0
        self._open_until = 0.0

    def record_failure(self) -> None:
        self._failures += 1
        self._open_until = time.time() + self.cooldown


class LLMClient:
    def __init__(self, config: Config):
        self.cfg = config
        self.breaker = CircuitBreaker(
            failure_threshold=config.get("llm.circuit.failure_threshold", 3),
            cooldown_seconds=config.get("llm.circuit.cooldown_seconds", 60),
        )
        self.max_tokens = config.get("llm.max_tokens", 1200)

    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        if not self.breaker.allow():
            logger.warning("熔断器开启中，直接降级")
            return FALLBACK_REPLY

        last_error: Optional[Exception] = None
        # 底座顺序：本地 Ollama -> 豆包方舟（若启用）
        for attempt in range(2):
            try:
                reply = await self._call_ollama(prompt, system)
                if reply:
                    self.breaker.record_success()
                    return reply
            except Exception as exc:  # noqa: BLE001 - 兜底容错
                last_error = exc
                logger.warning("Ollama 调用失败：%s", exc)

            if self.cfg.get("llm.doubao.enabled", False):
                try:
                    reply = await self._call_doubao(prompt, system)
                    if reply:
                        self.breaker.record_success()
                        return reply
                except Exception as exc:  # noqa: BLE001
                    last_error = exc
                    logger.warning("豆包方舟调用失败：%s", exc)

            await asyncio.sleep(0.5)

        self.breaker.record_failure()
        if last_error:
            logger.error("全部底座不可用：%s", last_error)
        return FALLBACK_REPLY

    # ---------- 本地 Ollama ----------
    async def _call_ollama(self, prompt: str, system: Optional[str]) -> str:
        base = self.cfg.get("llm.ollama.base_url", "http://localhost:11434")
        model = self.cfg.get("llm.ollama.model", "qwen2.5:3b")
        timeout = self.cfg.get("llm.ollama.timeout", 30)
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{base}/api/generate",
                json={"model": model, "prompt": full_prompt, "stream": False},
            )
            resp.raise_for_status()
            data = resp.json()
            return (data.get("response") or "").strip()

    # ---------- 豆包方舟（火山引擎） ----------
    async def _call_doubao(self, prompt: str, system: Optional[str]) -> str:
        endpoint = self.cfg.get("llm.doubao.endpoint")
        api_key = self.cfg.get("llm.doubao.api_key", "")
        model = self.cfg.get("llm.doubao.model", "doubao-pro-4k")
        timeout = self.cfg.get("llm.doubao.timeout", 30)
        if not api_key:
            raise RuntimeError("豆包已启用但未配置 ARK_API_KEY")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": self.max_tokens,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
