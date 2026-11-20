# 接口文档

基础地址：`http://localhost:8000`

## GET /health

内核健康快照。

```json
{
  "name": "DaoNovice",
  "hexagram": "地正合",
  "samadhi": 0.92,
  "breath": 128,
  "adaptive_interval": 8,
  "indicators": {"cpu": 0.12, "memory": 0.34, "disk_io": 0.0, "network": 0.0, "ollama_latency": 0.5, "process_count": 0.21},
  "plugins": ["HealthCheck", "内修门", "内观门", "内建门", "内守门", "外传门", "外化门", "外用门", "外济门", "共生门"],
  "plugin_errors": {}
}
```

## GET /chat?msg=

共生对话。内核先做共生脉冲，再调用 LLM 底座生成应答。

| 参数 | 类型 | 说明 |
|------|------|------|
| msg | string | 用户言说 |

```json
{
  "reply": "道枢长转，行者无疆。",
  "hexagram": "地正合",
  "samadhi": 0.92
}
```

## GET /deep/status

九层深化全量总览：一体、两仪、三空、四象、五蕴、六合、七层、八卦、九卦，以及脉冲呼吸、十二自、三空约束、六项指标、六合觉知、七脉轮、卦象八门、共生深度、近期卦象历史。

## GET /deep/gate-control

当前卦象对应的八门开合指令。

```json
{
  "hexagram": "地正合",
  "open_gates": ["外传门", "外用门", "外化门", "外济门"],
  "gate_commands": {
    "内修门": "deactivate",
    "内观门": "deactivate",
    "内建门": "deactivate",
    "内守门": "deactivate",
    "外传门": "activate",
    "外化门": "activate",
    "外用门": "activate",
    "外济门": "activate"
  }
}
```

## GET /deep/auto-agent?need=

根据自然语言需求自动生成子 Agent 的 NLP 七层定义；先匹配内置模板，再尝试 LLM 解析 JSON，失败走兜底模板。

```json
{
  "agent_name": "MindfulGuide",
  "nlp_layers": {"精神": "...", "身份": "...", "信念": "...", "能力": [], "行为": [], "环境": "", "身体": ""},
  "status": "template_match"
}
```

## GET /1to9/summary

1–9 体系分层数据总览。

## GET /dashboard

可视化仪表盘（深色禅意风格，2 秒自动轮询）。

## 插件命令调用

插件能力通过内核 `on_command` 暴露，后续可在 API 层封装 `/plugins/{name}/command`。当前示例命令：

| 插件 | command | 关键参数 |
|------|---------|----------|
| 内修门 | `consult_sage` | `problem`, `thinkers` |
| 内观门 | `start_retreat` / `end_retreat` | `reason` / `insight` |
| 内建门 | `memory_store` / `memory_recall` | `layer`, `key`, `value` |
| 内守门 | `approve` | `action`, `causal_chain` |
| 外传门 | `write_full` | `topic`, `style` |
| 外化门 | `zen_reflection` | `state` |
| 外用门 | `create_agent` | `name`, `spirit`, `identity`, `belief` |
| 外济门 | `federation_join` | `node_id`, `address` |
| 共生门 | `she_is_here` | `message`, `mood` |
