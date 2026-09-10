"""本機控制橋接：HTTP API + WebSocket，供 OBS 瀏覽器來源與外部程式共用。

啟動：
  uv run python tools/control_bridge.py
  uv run python tools/control_bridge.py --port 28888 --root .

OBS Browser Source URL 範例：
  http://127.0.0.1:28888/?mode=obs
  （或 GitHub Pages）https://USER.github.io/REPO/?mode=obs&bridge=1

外部程式：
  curl -X POST http://127.0.0.1:28888/api/roll -H "Content-Type: application/json" -d "{\"direction\":\"top\"}"
"""

from __future__ import annotations

import argparse
import asyncio
import json
import mimetypes
import sys
from pathlib import Path
from typing import Any

from aiohttp import WSMsgType, web

ROOT = Path(__file__).resolve().parents[1]
clients: set[web.WebSocketResponse] = set()


def cli_result(
    *,
    ok: bool,
    command: str,
    artifacts: dict[str, Any] | None = None,
    metrics: dict[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    return {
        "ok": ok,
        "command": command,
        "artifacts": artifacts or {},
        "metrics": metrics or {},
        "error": error,
    }


async def broadcast(payload: dict[str, Any]) -> int:
    raw = json.dumps(payload, ensure_ascii=False)
    dead: list[web.WebSocketResponse] = []
    sent = 0
    for ws in clients:
        if ws.closed:
            dead.append(ws)
            continue
        try:
            await ws.send_str(raw)
            sent += 1
        except ConnectionError:
            dead.append(ws)
    for ws in dead:
        clients.discard(ws)
    return sent


async def ws_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse(heartbeat=30)
    await ws.prepare(request)
    clients.add(ws)
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                except json.JSONDecodeError:
                    continue
                # 轉發給其他客戶端（控制端 ↔ overlay）
                raw = msg.data
                for other in list(clients):
                    if other is ws or other.closed:
                        continue
                    try:
                        await other.send_str(raw)
                    except ConnectionError:
                        clients.discard(other)
                # 也接受來自控制端的指令物件
                if isinstance(data, dict) and data.get("source") != "overlay":
                    t = data.get("type") or data.get("action")
                    if t in {"dice.roll", "roll", "dice.set_direction", "dice.set_theme"}:
                        pass  # 已轉發
            elif msg.type in (WSMsgType.ERROR, WSMsgType.CLOSE):
                break
    finally:
        clients.discard(ws)
    return ws


def normalize_values(raw: Any) -> list[int] | None:
    if raw is None:
        return None
    if isinstance(raw, str):
        parts = [p for p in raw.replace(",", " ").split() if p]
    elif isinstance(raw, (list, tuple)):
        parts = list(raw)
    else:
        return None
    out: list[int] = []
    for p in parts:
        try:
            n = int(p)
        except (TypeError, ValueError):
            continue
        if 1 <= n <= 6:
            out.append(n)
    return out or None


async def api_roll(request: web.Request) -> web.Response:
    try:
        body = await request.json()
    except Exception:
        body = {}
    if not isinstance(body, dict):
        body = {}
    payload: dict[str, Any] = {"type": "dice.roll"}
    if body.get("direction"):
        payload["direction"] = body["direction"]
    if body.get("theme"):
        payload["theme"] = body["theme"]
    values = normalize_values(body.get("values"))
    if values:
        payload["values"] = values
    sent = await broadcast(payload)
    result = cli_result(
        ok=True,
        command="roll",
        artifacts={"payload": payload},
        metrics={"clients": len(clients), "sent": sent},
    )
    return web.json_response(result)


async def api_command(request: web.Request) -> web.Response:
    try:
        body = await request.json()
    except Exception:
        return web.json_response(
            cli_result(ok=False, command="command", error="invalid json"),
            status=400,
        )
    if not isinstance(body, dict):
        return web.json_response(
            cli_result(ok=False, command="command", error="body must be object"),
            status=400,
        )
    sent = await broadcast(body)
    return web.json_response(
        cli_result(
            ok=True,
            command="command",
            artifacts={"payload": body},
            metrics={"clients": len(clients), "sent": sent},
        )
    )


async def api_status(_request: web.Request) -> web.Response:
    return web.json_response(
        cli_result(
            ok=True,
            command="status",
            metrics={"clients": len(clients)},
        )
    )


def make_static_handler(root: Path):
    async def static_handler(request: web.Request) -> web.StreamResponse:
        rel = request.match_info.get("path", "") or "index.html"
        # 安全：禁止跳出 root
        target = (root / rel).resolve()
        if not str(target).startswith(str(root.resolve())):
            raise web.HTTPForbidden()
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file():
            # SPA / 預設首頁
            if rel in ("", "/"):
                target = root / "index.html"
            else:
                raise web.HTTPNotFound()
        ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        return web.FileResponse(target, headers={"Content-Type": ctype})

    return static_handler


def build_app(root: Path) -> web.Application:
    app = web.Application()
    app.router.add_get("/ws", ws_handler)
    app.router.add_get("/api/status", api_status)
    app.router.add_post("/api/roll", api_roll)
    app.router.add_post("/api/command", api_command)
    static = make_static_handler(root)
    app.router.add_get("/", static)
    app.router.add_get("/{path:.*}", static)
    return app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Skymiku Dice 本機控制橋接")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=28888)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="靜態檔根目錄（預設專案根）",
    )
    parser.add_argument("--json", action="store_true", help="啟動成功時輸出 JSON")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if not (root / "index.html").is_file():
        err = f"找不到 index.html：{root}"
        if args.json:
            print(json.dumps(cli_result(ok=False, command="serve", error=err), ensure_ascii=False))
        else:
            print(err, file=sys.stderr)
        return 1

    app = build_app(root)

    async def _run() -> None:
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, args.host, args.port)
        await site.start()
        info = cli_result(
            ok=True,
            command="serve",
            artifacts={
                "url": f"http://{args.host}:{args.port}/",
                "obs": f"http://{args.host}:{args.port}/?mode=obs",
                "ws": f"ws://{args.host}:{args.port}/ws",
                "roll": f"http://{args.host}:{args.port}/api/roll",
            },
            metrics={"port": args.port},
        )
        if args.json:
            print(json.dumps(info, ensure_ascii=False))
        else:
            print("Skymiku Dice bridge 已啟動")
            print(f"  控制台: {info['artifacts']['url']}")
            print(f"  OBS:    {info['artifacts']['obs']}")
            print(f"  WS:     {info['artifacts']['ws']}")
            print(f"  擲骰:   POST {info['artifacts']['roll']}")
        while True:
            await asyncio.sleep(3600)

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
