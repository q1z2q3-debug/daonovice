#!/bin/bash
# 停止 DaoNovice
set -u

APP_DIR="${APP_DIR:-/opt/daonovice}"
PID_FILE="$APP_DIR/daonovice.pid"

if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE")"
  kill "$PID" 2>/dev/null || true
  rm -f "$PID_FILE"
  echo "已停止 PID=$PID"
else
  pkill -f "daonovice.main" 2>/dev/null || true
  echo "未找到 PID 文件，已按进程名清理"
fi
