# Skymiku Dice

多方向 3D 骰子動畫：可當一般網頁玩，也可給 **OBS Browser Source** 擷取，並用本機程式／熱鍵遠端觸發擲骰。

整合自最完整版功能：多方向投擲、物理參數、主題、音效、結果顯示、設定儲存，以及外部控制橋接。

## 線上網頁

部署於 GitHub Pages（推送後約一分鐘生效）：

- 一般：`https://skymiku39.github.io/dice/`
- OBS 透明層：`https://skymiku39.github.io/dice/?mode=obs`

## 功能一覽

- 四方向投擲（上／下／左／右）與物理參數（速度、距離、重力）
- 五種主題、點數／圓角／音量可調，設定寫入 `localStorage`
- 碰撞音效（Web Audio + HTML Audio 備援）
- 擲骰結果顯示
- **OBS 模式**：透明背景、隱藏控制面板
- **程式控制**：WebSocket 橋接、HTTP API、`window.SkymikuDice`、`postMessage`、`BroadcastChannel`

## OBS 擷取 + 程式呼叫（可以，而且建議這樣做）

OBS 的 Browser Source 是**獨立 Chromium**，與你平常開的 Chrome **不共用** `localStorage`／`BroadcastChannel`。  
因此「網頁給 OBS 看」和「本機程式去按擲骰」要靠 **本機 WebSocket／HTTP 橋接** 串起來：

```
[本機程式 / curl / Stream Deck]
        │  POST /api/roll
        ▼
[control_bridge :28888]  ←── WebSocket ──→  [OBS Browser Source ?mode=obs]
        │
        └── 也可順便提供靜態頁 http://127.0.0.1:28888/
```

### 建議工作流

1. 在專案根目錄啟動橋接：

```powershell
cd D:\skymiku\dice
uv sync
uv run python tools/control_bridge.py --json
# 預設埠 28888（避開 Windows 保留的 8765）
```

2. OBS → 來源 → 瀏覽器 → URL：

```
http://127.0.0.1:28888/?mode=obs
```

勾選「重新載入時關閉來源」「控制音訊」依需求調整；背景會是透明。

3. 本機程式觸發：

```powershell
# 隨機擲
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:28888/api/roll -ContentType "application/json" -Body "{}"

# 指定方向與點數
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:28888/api/roll -ContentType "application/json" -Body '{"direction":"left","values":[6,6,6]}'
```

或：

```powershell
.\examples\roll.ps1
.\examples\roll.ps1 -Direction top -Values "1,2,3"
```

### 也可只用 GitHub Pages + 橋接

OBS URL：

```
https://skymiku39.github.io/dice/?mode=obs&bridge=1
```

頁面會連到 `ws://127.0.0.1:28888/ws`（仍需本機跑 bridge）。現代瀏覽器允許 HTTPS 頁連本機 WS（localhost 例外）。

### 其他控制方式

| 方式 | 適用 | 說明 |
|------|------|------|
| HTTP `POST /api/roll` | 任意本機程式 | 推薦 |
| WebSocket `/ws` | 自訂客戶端 | JSON：`{"type":"dice.roll",...}` |
| URL 參數 | 單次／測試 | `?mode=obs&roll=1&direction=top&values=1,2,3` |
| `window.SkymikuDice.roll()` | 同頁／DevTools | 瀏覽器主控台 |
| `postMessage` | iframe 父頁 | `{type:"dice.roll"}` |
| `BroadcastChannel("skymiku-dice")` | 同瀏覽器多頁 | **無法**打進 OBS 內嵌瀏覽器 |

## URL 參數

| 參數 | 例 | 說明 |
|------|----|------|
| `mode` | `obs` / `overlay` | 透明背景、隱藏 UI |
| `bridge` | `1` 或 `ws://127.0.0.1:28888/ws` | 連本機橋接（`mode=obs` 時預設開啟，`bridge=0` 關閉） |
| `direction` | `top`/`bottom`/`left`/`right` | 初始方向 |
| `theme` | `classic`/`dark`/`wooden`/`ocean`/`neon` | 主題 |
| `values` | `1,2,3` | 下一次（或搭配 `roll=1`）指定點數 |
| `roll` | `1` | 載入後自動擲一次 |
| `hideResults` | `1` | 隱藏結果條 |
| `debug` | `1` | 顯示 API 狀態徽章 |

## 遙控面板

橋接啟動後開啟：

- `http://127.0.0.1:28888/control.html`（給主播／助理按的控制頁）
- OBS 用 `http://127.0.0.1:28888/?mode=obs`

## 目錄

```
dice/
├── index.html              # 主程式（Pages / OBS 入口）
├── control.html            # 遙控面板
├── config/dice-config.json # 視覺／物理／音效設定
├── voice/clips/            # 碰撞音效
├── tools/control_bridge.py # 本機 HTTP + WebSocket 橋接
├── examples/roll.ps1       # 呼叫範例
└── pyproject.toml          # uv 依賴（aiohttp）
```

## 開發

```powershell
# 僅靜態（無遠端控制）
npx --yes serve .

# 完整（靜態 + API）
uv sync
uv run python tools/control_bridge.py
```

## 授權

個人／直播用途自由使用。
