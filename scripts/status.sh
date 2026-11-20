#!/bin/bash
# 查看 DaoNovice 运行状态与健康快照
set -u

APP_DIR="${APP_DIR:-/opt/daonovice}"
PID_FILE="$APP_DIR/daonovice.pid"
PORT="${PORT:-8000}"

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "✅ 运行中 PID=$(cat "$PID_FILE")"
  echo "--- 健康快照 ---"
  curl -s "http://localhost:${PORT}/health" || echo "接口暂不可达"
  echo
else
  echo "❌ 未运行"
  exit 1
fi
