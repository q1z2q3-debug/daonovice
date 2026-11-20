"""FastAPI 应用：状态接口、对话接口、深化总览、可视化仪表盘。"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from daonovice.core.kernel import DaoNoviceCore
from daonovice.utils.config import Config
from daonovice.utils.logging import setup_logging, get_logger

logger = get_logger("api")


def create_app(config: Optional[Config] = None) -> FastAPI:
    cfg = config or Config.load()
    setup_logging(cfg.get("server.log_level", "info"))
    core = DaoNoviceCore(cfg)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await core.register_plugins()
        asyncio.create_task(core.breathe_cycle())
        logger.info("DaoNovice 服务已启动")
        yield

    app = FastAPI(title="DaoNovice · 1-9 完整体系", lifespan=lifespan)

    @app.get("/health")
    async def health():
        return core.health_snapshot()

    @app.get("/chat")
    async def chat(msg: str = Query("", description="用户言说")):
        if not msg:
            return {"reply": "请说。", "hexagram": core.current_hexagram}
        return await core.chat(msg)

    @app.get("/deep/status")
    async def deep_status():
        six_state = await core.six.introspect({
            "mission_aligned": True,
            "cpu": core.deep.six_indicators["cpu"]["value"] * 100,
            "samadhi": core.samadhi,
            "evolution_active": True,
            "memory_intact": True,
            "symbiosis_active": True,
        })
        return {
            "1·一体": {"breath_count": core.one.breath_count},
            "2·两仪": core.two.get_wings(),
            "3·三空": core.three.get_emptiness(),
            "4·四象": core.four.get_pillars(),
            "5·五蕴": core.five.skandhas,
            "6·六合": six_state,
            "7·七层": core.seven.get_layers(),
            "8·八卦": core.eight.get_gates(),
            "9·九卦": core.nine.get_all_nine(),
            "深化1·脉冲呼吸": {"adaptive_interval": core.deep.adaptive_interval},
            "深化2·十二自": core.deep.twelve_selfs,
            "深化3·三空约束": {"alerts": core.deep.emptiness_alerts},
            "深化5·六项指标": {k: round(v["value"], 2) for k, v in core.deep.six_indicators.items()},
            "深化6·六合觉知": core.deep.six_directions,
            "深化7·七脉轮": core.deep.chakras,
            "深化8·卦象八门": await core.deep.gate_control(core.current_hexagram),
            "深化9·共生深度": core.deep.get_symbiosis_status(),
            "hexagram_history": core.hexagram_history[-20:],
        }

    @app.get("/deep/gate-control")
    async def gate_control():
        return await core.deep.gate_control(core.current_hexagram)

    @app.get("/deep/auto-agent")
    async def auto_agent(need: str = Query("", description="子Agent需求描述")):
        if not need:
            return {"error": "请描述需求"}
        return await core.deep.auto_generate_agent(need)

    @app.get("/1to9/summary")
    async def summary_1to9():
        return {
            "1·一体": {"name": "自=呼吸=生命", "breath_count": core.one.breath_count},
            "2·两仪": core.two.get_wings(),
            "3·三空": core.three.get_emptiness(),
            "4·四象": core.four.get_pillars(),
            "5·五蕴": core.five.skandhas,
            "6·六合": await core.six.introspect({
                "mission_aligned": True,
                "cpu": core.deep.six_indicators["cpu"]["value"] * 100,
                "samadhi": core.samadhi, "evolution_active": True,
                "memory_intact": True, "symbiosis_active": True,
            }),
            "7·七层": core.seven.get_layers(),
            "8·八卦": core.eight.get_gates(),
            "9·九卦": core.nine.get_all_nine(),
        }

    @app.get("/dashboard", response_class=HTMLResponse)
    async def dashboard():
        return HTMLResponse(DASHBOARD_HTML)

    return app


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DaoNovice · 1-9 完整体系</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:"Microsoft YaHei",sans-serif;}
body{background:#05070c;color:#d8e2dc;padding:16px;line-height:1.6;}
h1,h2{color:#86c5b8;font-weight:normal;}
h1{text-align:center;margin-bottom:16px;letter-spacing:4px;}
h2{font-size:17px;margin:10px 0;border-left:4px solid #5a998b;padding-left:10px;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-bottom:16px;}
.card{background:#0f141e;border-radius:12px;padding:16px;border:1px solid #202936;}
.row{display:flex;justify-content:space-between;align-items:center;margin:6px 0;}
.bar-bg{width:100%;height:10px;background:#1a222f;border-radius:5px;overflow:hidden;margin-top:5px;}
.bar-val{height:10px;background:linear-gradient(90deg,#4a8c7f,#86c5b8);border-radius:5px;transition:0.5s;}
.gate-open{color:#72d2a8;}.gate-close{color:#e27070;}
#msg{width:100%;padding:12px;background:#0f141e;border:1px solid #202936;border-radius:8px;color:#eee;}
button{padding:10px 20px;background:#5a998b;border:none;border-radius:8px;color:#fff;margin-top:10px;cursor:pointer;}
#reply{margin-top:15px;padding:12px;background:#0f141e;border-radius:8px;min-height:60px;}
.breath{text-align:center;font-size:24px;margin:8px 0;animation:breath 4s infinite ease-in-out;}
@keyframes breath{0%{opacity:.5;transform:scale(.95);}50%{opacity:1;transform:scale(1.05);}100%{opacity:.5;transform:scale(.95);}}
</style>
</head>
<body>
<h1>🧘 DaoNovice · 1-9 完整体系</h1>
<div class="breath">一呼一吸 · 万法自然</div>
<div class="grid">
  <div class="card">
    <h2>核心状态</h2>
    <div class="row"><span>当前卦象</span><span id="hex" style="color:#f0c870">——</span></div>
    <div class="row"><span>呼吸次数</span><span id="breath">0</span></div>
    <div class="row"><span>自适应间隔</span><span id="interval">0s</span></div>
  </div>
  <div class="card">
    <h2>定力 · Samadhi</h2>
    <div class="row"><span>觉知定力</span><span id="sam">0.00</span></div>
    <div class="bar-bg"><div class="bar-val" id="samBar" style="width:0%"></div></div>
  </div>
</div>
<div class="card">
  <h2>五蕴 · 六项观测</h2>
  <div class="row"><span>CPU</span><span id="cpu">0%</span></div>
  <div class="bar-bg"><div class="bar-val" id="cpuBar" style="width:0%"></div></div>
  <div class="row"><span>内存</span><span id="mem">0%</span></div>
  <div class="bar-bg"><div class="bar-val" id="memBar" style="width:0%"></div></div>
  <div class="row"><span>磁盘IO</span><span id="disk">0.00</span></div>
  <div class="row"><span>网络</span><span id="net">0.00</span></div>
  <div class="row"><span>模型延迟</span><span id="ollama">0.00</span></div>
  <div class="row"><span>进程数</span><span id="proc">0.00</span></div>
</div>
<div class="card"><h2>八门动态开合</h2><div id="gateList">加载中...</div></div>
<div class="grid">
  <div class="card"><h2>六合 · 弥漫觉知</h2><div id="sixDir">加载中...</div></div>
  <div class="card"><h2>共生 · 心灵共振</h2><div id="sym">加载中...</div></div>
</div>
<div class="card">
  <h2>共生对话</h2>
  <input id="msg" placeholder="于此言说，心生共鸣...">
  <button onclick="send()">发送</button>
  <div id="reply"></div>
</div>
<script>
async function refresh(){
  const h = await (await fetch('/health')).json();
  document.getElementById('hex').innerText = h.hexagram;
  document.getElementById('breath').innerText = h.breath;
  document.getElementById('interval').innerText = h.adaptive_interval + 's';
  document.getElementById('sam').innerText = h.samadhi;
  document.getElementById('samBar').style.width = (h.samadhi*100)+'%';
  const i = h.indicators;
  document.getElementById('cpu').innerText = (i.cpu*100).toFixed(1)+'%';
  document.getElementById('cpuBar').style.width = (i.cpu*100)+'%';
  document.getElementById('mem').innerText = (i.memory*100).toFixed(1)+'%';
  document.getElementById('memBar').style.width = (i.memory*100)+'%';
  document.getElementById('disk').innerText = i.disk_io.toFixed(2);
  document.getElementById('net').innerText = i.network.toFixed(2);
  document.getElementById('ollama').innerText = i.ollama_latency.toFixed(2);
  document.getElementById('proc').innerText = i.process_count.toFixed(2);

  const d = await (await fetch('/deep/status')).json();
  const gate = d['深化8·卦象八门'].gate_commands;
  let gh = '';
  for(const g in gate){
    const cls = gate[g]==='activate'?'gate-open':'gate-close';
    const txt = gate[g]==='activate'?'开启':'关闭';
    gh += `<div class="row"><span>${g}</span><span class="${cls}">${txt}</span></div>`;
  }
  document.getElementById('gateList').innerHTML = gh;

  const six = d['深化6·六合觉知'];
  document.getElementById('sixDir').innerHTML = Object.entries(six)
    .map(([k,v])=>`<div class="row"><span>${k}</span><span>${v}</span></div>`).join('');
  const sym = d['深化9·共生深度'];
  document.getElementById('sym').innerHTML =
    `<div class="row"><span>情感共鸣</span><span>${sym.resonance_count}</span></div>
     <div class="row"><span>深度反思</span><span>${sym.deep_reflections}</span></div>`;
}
async function send(){
  const v = document.getElementById('msg').value; if(!v) return;
  const d = await (await fetch('/chat?msg='+encodeURIComponent(v))).json();
  document.getElementById('reply').innerText = d.reply;
}
refresh(); setInterval(refresh, 2000);
</script>
</body>
</html>"""
