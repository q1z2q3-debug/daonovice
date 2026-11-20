"""服务入口：python -m daonovice.main"""
from __future__ import annotations

import uvicorn

from daonovice.api.app import create_app
from daonovice.utils.config import Config


def main() -> None:
    cfg = Config.load()
    app = create_app(cfg)
    uvicorn.run(
        app,
        host=cfg.get("server.host", "0.0.0.0"),
        port=int(cfg.get("server.port", 8000)),
        log_level=cfg.get("server.log_level", "info"),
    )


if __name__ == "__main__":
    main()
