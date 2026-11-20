#!/bin/bash
# ============================================================
# DaoNovice · 从零一键部署（Ubuntu/Debian，WSL2 兼容）
# 用法：sudo bash deploy/deploy_from_scratch.sh
# 说明：不使用全局 set -e，关键步骤显式判断，避免单点失败中断全程
# ============================================================
set -u
export DEBIAN_FRONTEND=noninteractive

APP_DIR=/opt/daonovice
LOG_DIR="$APP_DIR/logs"
mkdir -p "$LOG_DIR"
exec > "$LOG_DIR/from_scratch_deploy.log" 2>&1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "===> [1/6] 系统依赖安装"
apt-get update -qq
apt-get install -y -qq --no-install-recommends \
  curl wget python3 python3-pip python3-venv sqlite3 redis-server ca-certificates || {
  echo "系统依赖安装出现警告，请查看日志"; }

echo "===> [2/6] 代码就位到 $APP_DIR"
mkdir -p "$APP_DIR"
cp -r "$REPO_ROOT/src" "$APP_DIR/"
cp -r "$REPO_ROOT/config" "$APP_DIR/"
cp "$REPO_ROOT/requirements.txt" "$APP_DIR/"

echo "===> [3/6] Python 虚拟环境"
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip -q
"$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/requirements.txt" || {
  echo "Python 依赖安装失败"; exit 1; }

echo "===> [4/6] Ollama 就绪检查（端口轮询，不再固定 sleep）"
if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh >/dev/null 2>&1 || echo "Ollama 安装失败，可稍后手动安装"
fi

if command -v ollama >/dev/null 2>&1; then
  pkill -f "ollama serve" 2>/dev/null || true
  nohup ollama serve >/dev/null 2>&1 &
  READY=0
  for _ in $(seq 1 30); do
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then READY=1; break; fi
    sleep 1
  done
  if [ "$READY" = "1" ]; then
    ollama pull qwen2.5:3b >/dev/null 2>&1 || echo "模型拉取失败，可稍后执行：ollama pull qwen2.5:3b"
  else
    echo "Ollama 端口 11434 未就绪，本地对话将走降级文案"
  fi
else
  echo "未检测到 Ollama，系统将以降级模式运行"
fi

echo "===> [5/6] Redis 缓存"
redis-server --daemonize yes 2>/dev/null || echo "Redis 启动失败（可选组件，不影响内核）"

echo "===> [6/6] 启动 DaoNovice"
APP_DIR="$APP_DIR" bash "$REPO_ROOT/scripts/start.sh"

IP="$(hostname -I | awk '{print $1}')"
PORT="$(grep -E '^\s*port:' "$APP_DIR/config/config.yaml" | awk '{print $2}')"
PORT="${PORT:-8000}"
echo ""
echo "════════════════════════════════════════════════════"
echo "  ✅ DaoNovice 部署完成"
echo "  🌐 仪表盘：http://${IP}:${PORT}/dashboard"
echo "  💬 对话：  http://${IP}:${PORT}/chat?msg=你好"
echo "  📊 状态：  http://${IP}:${PORT}/health"
echo "  📁 目录：  $APP_DIR"
echo "════════════════════════════════════════════════════"
