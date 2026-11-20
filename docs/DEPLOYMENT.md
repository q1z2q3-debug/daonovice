# 部署与排障手册

## 一、环境要求

- Ubuntu 20.04+ / Debian 12+ / WSL2（Ubuntu）
- Python 3.11+
- 可选：Ollama（本地模型）、Redis（缓存）
- 最低 2GB 内存；运行 `qwen2.5:3b` 建议 4GB 以上

## 二、从零部署

```bash
sudo bash deploy/deploy_from_scratch.sh
```

脚本会依次完成：系统依赖 → 代码就位 → Python 虚拟环境 → Ollama 端口轮询就绪 → Redis → 启动服务。

### 以 systemd 方式托管（生产推荐）

```bash
sudo cp deploy/daonovice.service /etc/systemd/system/daonovice.service
sudo systemctl daemon-reload
sudo systemctl enable --now daonovice
sudo systemctl status daonovice
```

## 三、本地开发

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m daonovice.main
```

## 四、接入豆包方舟（可选远端底座）

1. 在火山引擎方舟控制台创建 API Key；
2. 写入环境变量（不要提交进仓库）：

```bash
export ARK_API_KEY="你的Key"
```

3. 编辑 `config/config.yaml`：

```yaml
llm:
  doubao:
    enabled: true
    model: doubao-pro-4k
```

## 五、常见问题

### 1. `setup.sh: $'\r': command not found`（Windows 换行符污染）

脚本在 Windows 记事本编辑后会带入 `\r`。修复：

```bash
sudo apt install -y dos2unix
dos2unix deploy/deploy_from_scratch.sh scripts/*.sh
```

后续编辑 `.sh` 请在 WSL 内使用 `nano` / `vim`。

### 2. `externally-managed-environment`

Debian/Ubuntu 保护系统 Python。部署脚本已使用虚拟环境；若手动 pip 安装，请先激活 venv，或加 `--break-system-packages`（仅本地调试）。

### 3. `Unable to locate package curl`

软件源未索引：

```bash
sudo apt update
```

### 4. Ollama 端口未就绪

部署脚本已改为端口轮询（最多等待 30 秒）。手动排查：

```bash
ollama serve &
curl http://localhost:11434/api/tags
ollama pull qwen2.5:3b
```

### 5. 端口被占用

```bash
bash scripts/stop.sh
pkill -f "ollama serve"
pkill -f uvicorn
```

### 6. 目录权限不足

```bash
sudo chown -R $USER:$USER /opt/daonovice
```

### 7. 查看运行日志

- 服务输出：`/opt/daonovice/logs/daonovice.out.log`
- 分级日志：`/opt/daonovice/logs/daonovice.log`
- 部署日志：`/opt/daonovice/logs/from_scratch_deploy.log`

## 六、WSL2 性能建议

在 Windows 用户目录创建 `.wslconfig` 限制资源、避免抢占宿主机：

```ini
[wsl2]
memory=8GB
processors=4
swap=2GB
```

工程数据放在 Linux 原生文件系统（`/opt/daonovice`），不要放在 `/mnt/c/` 跨挂载目录，以避免 IO 延迟与换行符问题。
