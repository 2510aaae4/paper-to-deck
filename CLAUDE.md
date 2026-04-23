# Paper-to-Deck · 專案使用說明

這個工作目錄存的是兩個相關的 skill——把學術論文 PDF 轉成乾淨可編輯的 PowerPoint 簡報。主要給自己未來用（lab meeting / journal club / 研討會的 slide 準備），也可以給同事。

---

## 目錄結構

```
.
├── README.md                 · 公開 repo 對外說明
├── LICENSE                   · MIT
├── CLAUDE.md                 · 本檔 · 給 Claude Code / 維護者的 orientation
├── .gitignore                · 排除 _private/、測試產出、第三方 licensed 素材
├── docs/plans/               · 設計文件 (brainstorming → writing-plans 產出)
├── start/                    · 入口 skill · 接收 PDF、驗證、遞交給主 skill
├── paper-to-deck/            · 主 skill · interview → outline → HTML → PPTX
└── _private/                 · 不進 repo · 本機測試產出、版權敏感檔、第三方 licensed 參考素材
```

兩個 skill 分開維護、各自有 `SKILL.md` 與 `CHANGELOG.md`。`start` 是窄入口（只做 PDF 驗證 + 交棒），`paper-to-deck` 是主體（interview、outline、slide 建構、PPTX 匯出全在這）。

**`_private/` 的約定**：任何來自某篇論文的 PDF、擷取圖 / 表、全文 dump、按特定論文產出的 deck / pptx，都放這裡。第三方 licensed 參考素材（e.g. 別人的 SKILL.md 鏡像）也放這裡。這個資料夾被 `.gitignore` 排除，永遠不進公開 repo。

---

## 標準工作流程 · 新論文從頭到尾

### Step 1 · 使用者呼叫 start
```
使用者：「start a paper」 / 「新的 paper 要做簡報」 / PowerShell 拖放路徑 `& '…\foo.pdf'`
```
`start` SKILL.md 的流程：greet → 問 PDF 路徑 → 跑 `start/scripts/validate_pdf.py` 驗 4 項（檔案存在 / 是 PDF / 有文字層 / 頁數 2–60）→ 交棒 `paper-to-deck`。

### Step 2 · paper-to-deck 擷取與面談
```
python paper-to-deck/scripts/extract_paper.py <pdf> --out-dir <project-dir>
```
產生 `paper.json` + `figures/` + `tables/` + `pages/` + `full_text.txt`。擷取器有五層：Tier 0 (docling) → Tier 1 (`get_images()`) → Tier 2 (caption-anchored crop) → Tier 2b (facing-page) → Tier 2c (landscape rotation) → Tier 3 (full-page fallback)。細節見 `paper-to-deck/references/pdf-extraction.md`。

擷取完後 agent 跑**結構化面談**（`references/interview.md`）：13 題（受眾 / 長度 / 互動 / 重點 / 個人連結 / 設計 / 語言×2 / 論文特定×4+ / **字體**）。Typography 永遠放**最後**一題，預設 Taipei Sans TC Beta。

### Step 3 · Outline（等 user 批）
依面談結果產 `outline.md`（22 張左右），user 批准後才動 slide。

### Step 4 · HTML 建構
先做前 2-3 張給 user 早期 feedback，再補完剩餘。HTML 支援 `←/→` 切、`N` 看 speaker notes、`F` 全螢幕、`Home/End` 跳首末。

### Step 5 · PPTX 匯出
`build_pptx.py`（deck-specific，非 skill shared）用 python-pptx 重建每張 slide 為可編輯文字方塊。16:9、13.33×7.5 in、Taipei Sans TC Beta + Microsoft JhengHei fallback。

### Step 6 · 交付
Final message 兩句以內：caveat（例：圖 3 是 placeholder、equation 4 是 raster）+ next step（在 PowerPoint 開、走一遍 speaker notes）。

---

## 硬性規則（skill-wide）

### 安全護欄（paper-to-deck D5）
- **不讀** `~/Downloads` / `~/Desktop` / 任何未經使用者指名的目錄
- **不 `curl`** 任意外部站——只能呼叫白名單內的 API
- **不自動啟動** huashu-design 式的品牌協議（paper 沒品牌）
- 允許的外部存取：
  1. 使用者指定的 PDF（本機檔案）
  2. docling 首次模型下載
  3. **白名單 public-asset API**（v0.5.0 新增，見 `paper-to-deck/references/public-imagery.md`）：
     - `commons.wikimedia.org/w/api.php`
     - `openi.nlm.nih.gov/api/search`
     - `phil.cdc.gov`
     - `www.who.int`（公開報告頁）
- License filter 預設**嚴格**（CC0 / CC BY / CC BY-SA / US-gov PD）；面談 Q17 可切寬鬆（加 CC BY-NC）
- 受版權的 pop-culture meme（Shrek、電影劇照⋯⋯）**agent 不 fetch**，只留 placeholder 由 user 手動貼

### 設計紀律（slides 1-N，cover 除外）
- **Slide title 是 statement 或 question，不是 topic label**
- **Body text ≤ 40 字 / slide**
- **不寫 `[12]` 這種編號引用**，用 `(Smith 2024)`
- **圖來源只能是該論文**（D3）；沒有圖就用 honest placeholder，不自己畫替代圖
- **不放 emoji / gradient / stock icon**
- **"Figure N" 不當 slide title / eyebrow**，attribution 退到圖下 caption

### Cover 例外
Cover slide 的主職是「讓聽眾立刻認出是哪篇論文」——**論文標題保留當大字**，不套 statement 規則。

### 語言
- 使用者預設**繁體中文**回應（含 skill template 翻譯）
- Slide 內容預設**英文**（面談問）· speaker notes 獨立設定（常為中文）
- 技術識別符（檔名、函式名、CLI flag）永遠英文

### Windows 寫程式
- `scripts/` 的 Python 腳本**只對 stdout 印 ASCII**（data 內容也要 sanitize——cp950 locale 會在 data 插入 ` ` 之類時炸）
- 第一行預設 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` 當保險
- `pymupdf` / `docling` 的安裝細節見 `paper-to-deck/references/windows-setup.md`

---

## 關鍵檔案快查

| 你想做的事 | 去讀這個 |
|---|---|
| 跟新使用者解釋這 skill | `start/SKILL.md` |
| 懂完整 workflow 紀律 | `paper-to-deck/SKILL.md` |
| 改擷取邏輯 | `paper-to-deck/scripts/extract_paper.py` + `references/pdf-extraction.md` + `references/external-extractors.md` |
| 改面談問題 | `paper-to-deck/references/interview.md` |
| 改 slide pattern / anti-slop | `references/slide-patterns.md` · `references/anti-slop-academic.md` |
| 調整醫學教學視覺（V1–V8、調色盤） | `references/slide-patterns.md`（下半）· `assets/themes/*.json` |
| 找 public-domain 圖 | `references/public-imagery.md` · `scripts/search_public_imagery.py` |
| 寫新 PPTX | 讀 `references/pptx-gotchas.md` 先——那六條雷都踩過 |
| Windows setup | `references/windows-setup.md` |
| 版本歷史 | `paper-to-deck/CHANGELOG.md`（每個版本的事件背景都有）|
| 回歸測試案例 | `paper-to-deck/evals/evals.json` |

---

## 開發紀律（給未來的 Claude / 我自己）

### 規則只能從事件長出
CHANGELOG 看一遍會發現：每條 rule 都有一個具體事件背書（cp950 第二次、letter-spacing × 100 bug、cover title 被 revert、NEJM landscape table）。**不要憑空加 rule**——等踩坑再加。a-priori 想像的 rule 會被使用者翻案。

### 新 paper 就是新 eval case
拿新論文（不同 publisher、不同格式、equation-heavy、arXiv、thesis...）就去加進 `evals/evals.json` 的 `candidate_next_evals`。每次跑完回寫觀察。

### docling 是可選的
`scripts/extract_paper.py` 在沒裝 docling 時完全退回手工 Tier 1-3。**不要把 docling 寫成 hard dependency**——它只是優化 Tier 0。

### 版本規劃
- 0.x = 還在迭代（目前是 v0.4.0）
- 1.0 保留給「在 ≥ 3 篇不同 paper 上成功跑過」
- 每個版本 bump 都要有 CHANGELOG 條目 + 事件背景

### CLAUDE.md（這份）的維護
變更原則：
- 加新 skill → 在目錄樹 + 工作流程加一段
- 加新 reference → 在「關鍵檔案快查」加一行
- 改 hard rule → 在「硬性規則」段落改
- **不要**把 CHANGELOG 內容複製來 CLAUDE.md——指過去就好

---

## 目前已知待辦

優先序列摘自 `paper-to-deck/CHANGELOG.md`「Unreleased」段：

1. 跑第三篇論文（建議 arXiv ML paper / Nature Letter / 雙語需求）以暴露新 bug
2. Skill 搬到 `~/.claude/skills/`（目前在 project 目錄）
3. File-size disparity 檢查寫進 `verification.md` Tier A
4. CrossRef DOI lookup 取代 `_guess_title` 的爛 heuristic
5. CW-rotated table 偵測（沒遇到、先等）
