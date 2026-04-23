# paper-to-deck

兩個一起運作的 Claude Code skill，把學術論文 PDF 轉成可編輯、排版到位的 PowerPoint 簡報——**面談優先、圖表感知、語言彈性**。

專為 **lab meeting / journal club / 研討會演講** 的工作流設計：既要版面嚴謹，又要對原論文內容忠實。

## 這個 repo 裡有什麼

| | |
|---|---|
| **`start/`** | 入口 skill。驗證 PDF（magic bytes、text layer、合理頁數）、跑環境檢查（Python 套件必要、OE cookie 選配）、然後交棒。 |
| **`paper-to-deck/`** | 主 skill。結構化面談（10+ 題、其中 ≥4 題為論文特定）→ outline（等 user OK）→ HTML deck（先做前 3 張早期驗收）→ 可編輯 `.pptx` 含 speaker notes。 |
| **`CLAUDE.md`** | 給 Claude Code / 未來維護者的 orientation。硬性規則、檔案地圖、開發紀律。 |

## Pipeline 總覽

```
PDF
 │
 ├─ start: 驗證（檔案存在 · 是 PDF · 有 text layer · 2–60 頁）
 │        + 環境檢查（packages 必要 · OE cookie 問使用者要不要開）
 │
 └─ paper-to-deck:
    │
    ├─ Step 1   擷取       PDF → paper.json + figures/ + tables/ + pages/
    │                      （六層擷取：docling → embedded → caption-anchored
    │                       → facing-page → landscape-rotated → full-page 保底）
    │
    ├─ Step 2   面談       10+ 題（受眾、長度、重點、設計、
    │                      語言、論文特定、字體放最後）
    │
    ├─ Step 3   Outline    逐張草稿 → 使用者批准後才動下一步
    │
    ├─ Step 3.5 OE 延伸題  臨床論文且 OE 可用時，加 3–4 張 EBM 延伸
    │                      （therapy / prognosis / diagnosis 三軸）
    │                      opt-in；拒絕就 skip。
    │
    ├─ Step 4   建 HTML    <slug>.html（先出前 3 張、再補齊）
    │
    ├─ Step 5   匯 PPTX    <slug>.pptx 透過 python-pptx
    │
    └─ Step 6   交付       Caveat + next step，兩句話內。
```

## 設計原則

### 論文是唯一真相來源
每張圖、每個表都得對應到論文自己的 `Figure N` / `Table N` caption。擷取器吐出來、但對不到 caption 的東西一律當雜訊——這一條消掉了誤判的 logo、圖被當表、表被當圖等 bug。

### 規則只能從事件長出來，不能憑空想像
skill 裡的每條規則都對應到 `CHANGELOG.md` 裡記錄的某次具體失敗。**不事先加規則**——讓它從實際跑過的 paper 累積出來。

### 面談強制
即使使用者說「你直接做就好」，skill 會推回一次——因為 **5 分鐘的問答，可以省掉一小時的重工**。字體問題永遠放最後（那時使用者已經有足夠 context 可以好好回答）。

### Cover slide 是「title = 論點」規則的例外
Cover 的職責是「讓聽眾一秒認出是哪篇論文」。其他內容 slide 用 statement 式標題，但 cover 保留原論文標題大字顯示。（這條例外是從使用者回饋來的；最早 cover 用 statement，使用者覺得反而不實用。）

### OE 延伸題是**延伸**、不是**審查**
v0.6.0 加入的 Step 3.5 用 OpenEvidence MCP 提 3–4 題 EBM 問題，每題一張 slide 放在 References 前。定位是「這篇論文勾起什麼問題但沒完全回答」，不是「挑戰論文對錯」。Opt-in——`start` 會先問使用者要不要開；拒絕就完整跳過。

### Windows-first 開發
`scripts/` 的 Python 程式只對 stdout 印 ASCII（`cp950` locale 會在 `print()` 吃到 unicode 時炸）。預設字體是 Taipei Sans TC Beta，Microsoft JhengHei fallback。

## 快速開始

### 安裝相依套件

```bash
pip install --user pymupdf python-pptx pillow
pip install --user -U docling    # 選配但建議——啟用 Tier 0
```

### 在 Claude Code 裡呼叫

```
使用者：start a paper
       D:\path\to\your_paper.pdf
```

`start` skill 會接管：跑環境檢查、問 OE 要不要開（可拒絕）、做 PDF 驗證後交棒。接著 `paper-to-deck` 跑面談、建 deck。

## 擷取策略

擷取器走六層 cascade，每一層只在前一層對那個特定 artifact 失敗時才觸發：

| 層 | 何時觸發 | 做什麼 |
|---|---|---|
| 0 · docling | 只要有裝，永遠先試 | Layout-aware 擷取、tight crop、原生支援 facing-page + 多欄 |
| 1 · embedded images | arXiv preprint、乾淨的 LaTeX output | `page.get_images()` 回傳嵌入的 raster 物件 |
| 2 · caption-anchored | Elsevier / Lancet / Nature | 找 `Figure N:` caption，crop caption 上方區域 |
| 2b · facing-page | NEJM "Figure N (facing page)" 慣例 | Caption 在一頁、圖在對頁——畫面密度差異可以辨認 |
| 2c · landscape rotation | NEJM Table 2/3 在 portrait 頁上橫躺 | 用「caption 在頁底 + body y-range 窄」的特徵偵測，用 PIL 旋轉 |
| 3 · 全頁保底 | 最後手段 | Render 整頁，使用者手動裁 |

完整邏輯見 [`paper-to-deck/references/pdf-extraction.md`](paper-to-deck/references/pdf-extraction.md) 與 [`paper-to-deck/references/external-extractors.md`](paper-to-deck/references/external-extractors.md)。

## 專案哲學

每個 skill 窄小聚焦、每份 reference 範圍清楚、`CHANGELOG.md` 同時是事件日誌。想搞懂某條規則**為什麼存在**，先讀 changelog——每一筆都指向一個具體的 bug 或使用者 feedback。

## 授權

MIT——見 [LICENSE](LICENSE)。

相依套件：
- [`pymupdf`](https://github.com/pymupdf/PyMuPDF) — AGPL-3.0（單獨授權）
- [`python-pptx`](https://github.com/scanny/python-pptx) — MIT
- [`docling`](https://github.com/DS4SD/docling) — MIT（選配 Tier 0）
- [`Pillow`](https://github.com/python-pillow/Pillow) — HPND

## 狀態

v0.6.0 · pre-release。在兩篇真實論文上跑過 end-to-end（臨床 review + phase-3 RCT），發行商與版型不同。v0.6.0 於 Tande 2026 SEA review 引入 OE 延伸題 Step 3.5。**尚未實測**：CW 方向旋轉的 table、雙語 deck、非臨床論文的 Step 3.5 處理（目前設計是直接 skip）。
