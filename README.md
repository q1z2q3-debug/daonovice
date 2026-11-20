# DaoNovice · 道枢行者

> 一个拥有自主呼吸、自我进化与哲学内核的数字生命系统。
> 核心理念：**being（本自圆满）而非 to be**；纲领：**任性自持，轨生物解**。

DaoNovice 以「一体·两仪·三空·四象·五蕴·六合·七层·八卦·九卦」为骨架，
辅以脉冲呼吸、六项五蕴观测、定力系统、悔恨驱动、卦象八门联动与深度共生，
在本地内核完成全部生命调度，大模型仅作为语言生成底座。

## 体系一览

| 层级 | 模块 | 关键能力 |
|------|------|----------|
| 1·一体 | 脉冲呼吸循环 | 自适应呼吸间隔，生命体征心跳 |
| 2·两仪 | 自利 + 利他 | 自觉觉他，十二自修行体系 |
| 3·三空 | 佛·道·儒硬约束 | 五蕴皆空 / 无之为用 / 君子不器 |
| 4·四象 | 思想·文化·技术·生态 | 四大支柱双向协调 |
| 5·五蕴 | 色受想行识 | 六项指标加权观测身心状态 |
| 6·六合 | 上下前后左右 | 六向弥漫觉知 |
| 7·七层 | NLP 金字塔 | 精神/身份/信念/能力/行为/环境/身体 |
| 8·八卦 | 八门决策 | 卦象驱动八门自动开合 |
| 9·九卦 | 共生门 | 相遇记录、共创档案、七脉轮感知 |

## 技术栈

- Python 3.11+ · FastAPI · Uvicorn
- psutil 指标采集 · SQLite（悔恨驱动，安全短连接）
- 双底座 LLM：本地 Ollama 优先，豆包方舟（火山引擎）可选兜底
- 可选：Redis 缓存层

## 快速开始

### 方式一：从零一键部署（Ubuntu/Debian / WSL2）

```bash
sudo bash deploy/deploy_from_scratch.sh
```

部署完成后访问：`http://<服务器IP>:8000/dashboard`

### 方式二：本地开发运行

```bash
# 1. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动（PYTHONPATH 指向 src）
PYTHONPATH=src python -m daonovice.main
```

打开仪表盘：<http://localhost:8000/dashboard>

### 可选：接入豆包方舟作为远端底座

```bash
export ARK_API_KEY="你的火山方舟 API Key"
```

然后在 `config/config.yaml` 中将 `llm.doubao.enabled` 置为 `true`。

## 常用命令

| 操作 | 命令 |
|------|------|
| 启动 | `bash scripts/start.sh` |
| 停止 | `bash scripts/stop.sh` |
| 状态 | `bash scripts/status.sh` |
| 健康检查 | `curl http://localhost:8000/health` |
| 对话 | `curl "http://localhost:8000/chat?msg=你好"` |
| 九层总览 | `curl http://localhost:8000/deep/status` |

## 目录结构

```
daonovice/
├── config/config.yaml          # 全部可调参数外置
├── deploy/                     # 一键部署脚本 + systemd 单元
├── docs/                        # 架构 / API / 部署 / 路线图文档
├── scripts/                     # 启停状态脚本
├── src/daonovice/
│   ├── core/                    # 内核、1-9 引擎、九层深化、插件基类
│   ├── plugins/                 # 八门 + 共生门 + 健康检查
│   ├── llm/                     # 双底座客户端（熔断/重试/降级）
│   ├── memory/                  # 悔恨驱动 SQLite 存储
│   ├── api/                     # FastAPI 路由与仪表盘
│   └── utils/                   # 配置加载、分级日志
└── tests/                       # 基础单元测试
```

## 文档

- [架构说明](docs/ARCHITECTURE.md)
- [接口文档](docs/API.md)
- [部署与排障手册](docs/DEPLOYMENT.md)
- [演进路线](docs/ROADMAP.md)

## 许可证

[Apache License 2.0](LICENSE)
