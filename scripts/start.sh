#!/bin/bash
# 启动 DaoNovice（PID 文件管理，避免孤儿进程）
set -u

APP_DIR="${APP_DIR:-/opt/daonovice}"
PID_FILE="$APP_DIR/daonovice.pid"
LOG_DIR="$APP_DIR/logs"
LOG_FILE="$LOG_DIR/daonovice.out.log"
mkdir -p "$LOG_DIR"

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "DaoNovice 已在运行，PID=$(cat "$PID_FILE")"
  exit 0
fi

cd "$APP_DIR"
PYTHONPATH="$APP_DIR/src" nohup "$APP_DIR/.venv/bin/python" -m daonovice.main >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
sleep 3

if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "✅ 启动成功 PID=$(cat "$PID_FILE")，日志：$LOG_FILE"
else
  echo "❌ 启动失败，请查看 $LOG_FILE"
  rm -f "$PID_FILE"
  exit 1
fi
