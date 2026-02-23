# 骰子多方向版 - 配置說明

## 📁 文件結構

```
html/
├── 骰子多方向版.html          # 主程式文件
└── config/
    ├── dice-config.json       # 參數配置文件
    └── README.md              # 本說明文件
```

## 🎮 新功能說明

### 1. **多方向投擲**
   - 支援從四個方向投擲骰子：上、下、左、右
   - 在左側控制面板選擇投擲方向
   - 骰子會從選定方向飛入場景中心區域

### 2. **可調整物理參數**
   - **初始速度**：控制骰子飛行的力度（100-500 px/s）
   - **投擲距離**：設定骰子起點到目標的距離（200-800 px）
   - **重力**：調整重力效果，影響下落速度（800-2000 px/s²）

### 3. **參數外部化**
   - 所有參數都存放在 `config/dice-config.json` 文件中
   - 可以透過編輯配置文件來自訂所有參數
   - 配置文件包含詳細的註釋說明

## ⚙️ 配置文件說明

### 視覺設定 (visual)

| 參數 | 預設值 | 範圍 | 說明 |
|------|--------|------|------|
| diceSize | 60 | 30-100 | 骰子尺寸（像素） |
| sceneWidth | 800 | 600-1200 | 場景寬度 |
| sceneHeight | 600 | 400-900 | 場景高度 |
| perspective | 2000 | 1000-3000 | 3D透視距離 |
| sceneRotationX | 30 | 0-60 | 場景俯視角度 |

### 物理設定 (physics)

| 參數 | 預設值 | 範圍 | 說明 |
|------|--------|------|------|
| initialVelocity | 300 | 100-500 | 初始速度 |
| throwDistance | 400 | 200-800 | 投擲距離 |
| gravity | 1200 | 800-2000 | 重力加速度 |
| pullHeight | 200-300 | - | 拉升高度範圍（隨機） |
| pullTime | 150-250 | - | 拉升時間範圍（隨機） |
| spinDuration | 1600-2400 | - | 旋轉持續時間範圍 |
| moveDuration | 1400-2000 | - | 移動持續時間範圍 |
| bounceFrequency | 2.2-3.2 | - | 彈跳頻率 |
| tiltAngle | -60 to 60 | - | 傾斜角度範圍 |

### 佈局設定 (layout)

| 參數 | 說明 |
|------|------|
| dicePositions | 三個骰子的目標位置座標 |
| targetSpread | 落點隨機偏移範圍（±40px） |

### 方向設定 (directions)

支援的方向：
- **top**：從上方投擲（預設）
- **bottom**：從下方投擲
- **left**：從左側投擲
- **right**：從右側投擲

每個方向都定義了起始偏移量 (startOffset)，用於計算骰子的起始位置。

### 動畫設定 (animation)

| 參數 | 預設值 | 說明 |
|------|--------|------|
| spinRotation | 1080 | 旋轉圈數（3圈）|
| shadowOpacity | 0.7 | 陰影最大不透明度 |
| shadowBlur | 10 | 陰影模糊程度 |

### 顏色設定 (colors)

| 參數 | 預設值 | 說明 |
|------|--------|------|
| background | #e5e5e5 | 背景顏色 |
| diceFace | #fff | 骰子面的顏色 |
| diceBorder | #ccc | 骰子邊框顏色 |
| normalDot | #333 | 一般點數的顏色 |
| specialDot | #d32f2f | 特殊點數的顏色（1和4） |

## 🔧 如何自訂參數

1. 打開 `config/dice-config.json` 文件
2. 找到要修改的參數
3. 修改 `value` 欄位的數值
4. 確保數值在建議的 `range` 範圍內
5. 保存文件
6. 重新載入網頁（F5）

### 示例：修改骰子尺寸

```json
"diceSize": {
  "value": 80,          // 改為 80px（原本是 60px）
  "description": "骰子尺寸（像素）",
  "range": "30-100",
  "unit": "px"
}
```

## 💡 使用技巧

### 調整投擲效果

1. **更快速的投擲**
   - 增加初始速度（400-500）
   - 減少移動持續時間（moveDuration 改為 1000-1500）

2. **更柔和的落地**
   - 減少重力（900-1000）
   - 增加彈跳頻率（bounceFrequency 改為 3.5-4.5）

3. **更遠的投擲距離**
   - 增加投擲距離（600-800）
   - 增加初始速度以匹配距離

4. **更多彈跳**
   - 增加彈跳頻率（3.5-5.0）
   - 增加拉升高度（pullHeight 改為 300-400）

## 🎯 進階設定

### 修改骰子排列

編輯 `layout.dicePositions` 來改變三個骰子的排列位置：

```json
"dicePositions": {
  "1": { "x": -200, "y": -100 },  // 左上
  "2": { "x": 0, "y": 0 },         // 中間
  "3": { "x": 200, "y": 100 }      // 右下
}
```

### 創建自訂投擲方向

在 `directions.offsets` 中添加新方向：

```json
"topLeft": {
  "description": "從左上角投擲",
  "startOffset": { "x": -0.7, "y": -0.7 }
}
```

然後在 HTML 中添加對應的按鈕。

## 🐛 疑難排解

**問題：配置文件無法載入**
- 確認 `config` 資料夾與 HTML 文件在同一目錄
- 檢查 `dice-config.json` 是否為有效的 JSON 格式
- 查看瀏覽器控制台（F12）的錯誤訊息

**問題：骰子不顯示**
- 檢查 `diceSize` 是否在合理範圍內（30-100）
- 確認 `sceneWidth` 和 `sceneHeight` 足夠大

**問題：投擲效果不理想**
- 調整 `initialVelocity` 和 `throwDistance` 的比例
- 確保 `gravity` 值不要太高或太低
- 嘗試調整 `moveDuration` 來改變整體速度感

## 📝 版本資訊

- **版本**：1.0
- **最後更新**：2026-01-26
- **相容性**：支援所有現代瀏覽器（Chrome, Firefox, Edge, Safari）

## 🎨 自訂主題範例

### 深色主題
```json
"colors": {
  "background": { "value": "#1a1a1a" },
  "diceFace": { "value": "#2d2d2d" },
  "diceBorder": { "value": "#444" },
  "normalDot": { "value": "#fff" },
  "specialDot": { "value": "#ff6b6b" }
}
```

### 藍色主題
```json
"colors": {
  "background": { "value": "#e3f2fd" },
  "diceFace": { "value": "#fff" },
  "diceBorder": { "value": "#90caf9" },
  "normalDot": { "value": "#1976d2" },
  "specialDot": { "value": "#f44336" }
}
```

---

**提示**：備份原始配置文件，以便隨時恢復預設設定！
