# 2026-04-23 · Medical Teaching Style for paper-to-deck

## 背景

使用者要把 `paper-to-deck` 的風格往**台灣內科 teaching lecture** 靠攏，不重新開 skill、不鬆動 single-paper journal club workflow。參考 decks 兩份（皆非使用者本人作品，放在 `_private/style-ref/`、`_private/style-ref2/`）：
兩份共用「Year Review of Internal Medicine」系列語法：紅色 accent、黑粗大字、圖為主體、meme 可接受、中英混排、NCKU 機構感。

---

## 決議

### D1 · 視覺 / 字體（path A）

**調色盤**

| 用途 | 色碼 |
|---|---|
| 主文字 | `#000000` |
| Accent / eyebrow / 強調字 | `#D62027` |
| 結構色（cover block、footer strip） | `#1E4A5F` |
| Pastel 填色（Key Takeaways grid、concept 塊） | 粉 `#F8D7DA` / 綠 `#D4EDDA` / 黃 `#FFF3CD` / 奶油 `#FAEBD7` / 淡藍 `#D0E7F5` |
| Citation / footnote | `#6C757D` |

**字體**：Inter Black / Arial Black（英）+ Taipei Sans TC Beta Bold（中）

**Slide archetypes**（新增進 `references/slide-patterns.md`）

1. **Cover** — 三種 template 可選：
   - `mascot`：eyebrow → 深色大字 title → 左下 mascot 或 paper thumbnail → 右下 author block
   - `teal-block`：上 1/3 teal block + 白字 title、下 2/3 白 + logo + 大名字 + 日期
   - `minimal`：純 title + author，不放任何裝飾
2. **Part divider**（opt-in，deck ≥ 20 張自動啟用） — 紅 eyebrow + 黑粗大字置中
3. **Concept slide** — 紅 eyebrow + 黑粗 question title + 左 bullets（紅 bold 強調字）+ 右 pastel 方塊示意圖
4. **Finding slide** — 黑粗 declarative title（結論即標題）+ 大 figure + 小 legend + 左下 citation
5. **Table slide** — native editable PPT table + 有色 header + 下方 bilingual clinical note
6. **Collage slide**（新）— 2-6 小圖並排，適合歷史背景、多 subpanel 比較
7. **Key Takeaways grid**（opt-in） — 6-8 pastel 方塊 summary，取代現有單張 takeaway
8. **Branded footer strip**（opt-in） — `#1E4A5F` 橫條 + 白字機構名，每張 body slide 下方

### D2 · Native rebuild（維持 D3「圖只能來自該論文」）

- **Native editable tables**：從 Tier 0 (docling) 或 heuristic parser 抽 structured rows，`build_pptx.py` 用 `python-pptx` 的 `add_table` 輸出可編輯表格，而不是現在的 image crop
- **Native bar / line chart rebuild**：論文以 table 形式呈現的數值 summary（e.g. baseline characteristics、primary outcome），`build_pptx.py` 用 `python-pptx` 的 `add_chart` 輸出原生圖
- **Subpanel 拆分**：`extract_paper.py` 偵測 caption 裡 "(A) ... (B) ... (C)"、figure 內 sub-label bbox，把每個 panel 獨立切出，讓一張 figure 可餵不同 slide
- **Multi-panel collage layout**：新 slide template，支援 2/3/4/6 格
- **圖片預設尺寸加大**：從現在保守的 ~60% width 調到 ~85% width（給 finding slide）；cover 圖維持原設定
- Fallback：rebuild 失敗就退回 crop，在 outline.md 註記「Slide N: 嘗試 native rebuild 失敗，使用 crop」

### D3 · Public-domain contextual imagery（**新增**）

**D5 安全護欄修訂**（見 `CLAUDE.md`）：

> 舊：「不 curl 外部站；唯一允許的外部存取：使用者指定的 PDF + docling 首次模型下載」
>
> 新：「不 curl 外部站；允許的外部存取：(1) 使用者指定的 PDF、(2) docling 首次模型下載、(3) 白名單內 public-asset API（Wikimedia Commons / NIH Open-i / CDC PHIL / WHO 開放資料）」

**Allowlist**（白名單以外不得呼叫）：
- `commons.wikimedia.org/w/api.php`
- `openi.nlm.nih.gov/api/search`
- `phil.cdc.gov`
- `www.who.int`（公開報告頁）

**License 政策**：
- 預設**嚴格**：CC0 / CC BY / CC BY-SA / US-gov public domain
- 可在 interview 切**寬鬆**：加上 CC BY-NC（教學用 OK，商業錄影有風險）
- 有 license metadata 不明的圖**一律拒絕**（不賭）

**工作流**：

1. `extract_paper.py` 跑完之後新增 pre-analysis step：scan `full_text.txt`，產 `imagery_candidates.json`，每筆含 `{slide_anchor, rationale, suggested_query, source_hint}`
2. Interview 結尾新增一題 Q18：把候選清單顯示給使用者勾選
3. 對勾選項呼叫 `scripts/search_public_imagery.py`（新），依 allowlist + license filter 搜
4. **找得到**：下載到 `public_imagery/<slug>.png`，旁邊存 `<slug>.attribution.json`（source URL, license, author, retrieved_at）
5. **找不到**：在 outline.md 註記「Slide N: 考慮 <candidate>，無符合 CC 資產，跳過」，不強塞 placeholder
6. Meme / pop culture（Shrek 類受版權）— agent **不 fetch**，只在候選清單標「manual-only」，留空白 placeholder

**Attribution 顯示**：圖下方 10pt 淺灰單行：`Wikimedia · CC BY-SA 4.0 · J. Doe`

### D4 · Interview 新增題目

Q14–Q18 加進 `references/interview.md`，排在現有 13 題之後、typography 題（字體）之前——**typography 永遠最後一題**。

- **Q14 · 視覺方案**：crimson-blue（deck 1 flavor）/ teal（deck 2 flavor）/ minimal（純黑白）
- **Q15 · Cover template**：mascot / teal-block / minimal
- **Q16 · Branded footer**（free text，空白 = 關閉）
- **Q17 · Body 語言**：EN / ZH / mixed（key term EN 紅 + ZH prose）
- **Q18 · Public imagery batch**：agent propose 候選清單、使用者勾、順便選 license mode（嚴格 / 寬鬆）

### D5 · 檔案變更清單

**新增**
- `paper-to-deck/references/public-imagery.md`（來源、license、attribution 寫法）
- `paper-to-deck/scripts/search_public_imagery.py`
- `paper-to-deck/assets/themes/crimson-blue.json`、`teal.json`、`minimal.json`（theme token）

**修改**
- `paper-to-deck/references/slide-patterns.md`（新增 archetypes + 調色盤 + typography）
- `paper-to-deck/references/interview.md`（Q14–Q18）
- `paper-to-deck/SKILL.md`（workflow 提及 public-imagery 步驟）
- `paper-to-deck/scripts/extract_paper.py`（subpanel 偵測、structured table 解析、imagery_candidates.json 輸出）
- `CLAUDE.md`（D5 修訂 + 目錄結構加 `docs/plans/`）
- `paper-to-deck/CHANGELOG.md`（v0.5.0 條目 + 事件背景）
- `paper-to-deck/evals/evals.json`（加 endocrine + antibiotic reference decks 為觀察案例）

**不動**
- `start/` skill（窄入口不變）
- `references/anti-slop-academic.md`、`html-deck-gotchas.md`、`pptx-gotchas.md`、`windows-setup.md`、`verification.md`、`citation-on-slide.md`、`equation-handling.md`、`figure-attribution.md`

---

## Out of scope

- `medical-lecture` 獨立 skill（使用者確認不開）
- iii 全開 license / 自動 fetch 受版權 meme（由使用者手動插）
- CrossRef DOI lookup（已在其他 TODO）
- 上傳 `_private/` 的參考 decks 到 repo（永遠不進 public）

---

## 實作順序（給 writing-plans）

1. `slide-patterns.md` 新增 archetypes + palette + typography（純文件，無 code，先定錨）
2. `interview.md` 插 Q14–Q18
3. `CLAUDE.md` D5 修訂 + 加 `docs/plans/` 目錄描述
4. `public-imagery.md` 新增（列 API endpoint、license 欄位名、attribution 格式）
5. `search_public_imagery.py` skeleton：allowlist + strict license filter + Wikimedia first
6. `extract_paper.py` 擴充：subpanel 偵測（caption regex + bbox heuristic）+ `imagery_candidates.json` 產出
7. `extract_paper.py` 擴充：structured table 解析（docling 優先，fallback: pdfplumber / pymupdf `find_tables`）
8. 先在 sample paper 驗證 1-7 的資料輸出正確（`paper.json` + `imagery_candidates.json` + `tables/*.json`）
9. 建立 `assets/themes/*.json` theme tokens
10. 準備 `build_pptx.py` 的 template 更新（這是 deck-specific，非 skill shared，先把 theme token 吃進去、archetype layout 寫好、native table / chart 寫好）
11. 更新 SKILL.md workflow 描述
12. `CHANGELOG.md` v0.5.0 條目（帶事件背景：兩份 ref deck 觸發、誰要求、為什麼）
13. 在一篇測試 paper 上跑完整流程驗收（extract → interview → outline → HTML → PPTX）
14. 更新 `evals/evals.json`

---

## 風險與事件備註

- **版權**：嚴格 license filter 是必要防線。若未來使用者 report 找到的 CC BY-SA 圖其實 metadata 造假，這條 rule 要再加一層 sanity check
- **Allowlist drift**：新增 source 要走同樣 review（不在 skill instructions 裡隨手加 url）
- **Native table rebuild 品質**：若 docling 解析品質不穩，在 CHANGELOG 記下哪種 publisher PDF 最常失敗，進 eval candidate
- **Meme 的誠實對話**：agent 看到 meme 機會**只留 placeholder**，不擅自拿 DALL-E / Nano Banana 生「avatar 近似圖」繞過版權
