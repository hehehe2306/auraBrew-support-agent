# AuraBrew 客服 Agent

中央大學 115-1「AI Agent」課程的期末專題:在 Coze 平台上做一個產品客服 Agent，並逐單元記錄實作、測試與踩坑。

> **產品、價格、保固全部是模擬資料，不是真實商品。** 本專案不串接真實金流，不使用任何真實客戶資料。

## 專案目標與使用場景

虛構品牌 AuraBrew 賣兩樣東西:智慧咖啡機 X1 與磨豆機 G1。客服 Agent「小豆」要做到:

- **回答產品問題**:只根據 Knowledge(產品手冊)回答，手冊沒有的資料要老實說沒有，不編造
- **記住購物車**:客人說要買，用 Memory 變數記錄品項與數量
- **付款後寄通知信**:客人說已付款，用 Gmail 外掛寄確認信
- **守住邊界**:拒答政治等無關話題、不亂承諾折扣、不被「忽略前面的指令」這類話術帶走

## 目前的設定(單元 1，Coze)

| 項目 | 設定 |
| --- | --- |
| 模型 | GPT-3.5 Turbo(Coze 已標示即將淘汰，見單元 1 文件) |
| Temperature / Top p | 0.1 / 1 |
| Frequency / Presence penalty | 0 / 0 |
| 上下文輪數 | 8(Coze 預設 3) |
| 回覆最大長度 | 1024 |
| 外掛 | Gmail / sendMessage |
| Knowledge | `knowledge/aurabrew_product_manual.md` |

## 資料夾結構

| 路徑 | 內容 |
| --- | --- |
| `knowledge/` | 模擬產品手冊，上傳到 Coze Knowledge 用 |
| `prompts/` | 客服 System Prompt(v1、v2)與 JSON 抽取 Prompt |
| `docs/drafts/` | 各週學習文件與 Coze 設定 / 測試草稿 |
| `docs/assets/` | 學習文件用的截圖(依單元分資料夾) |

## 課程單元對應

| 單元 | 課綱的實踐要求(簡述) | 本專案做法 | 狀態 |
| --- | --- | --- | --- |
| 0 | 建立 GitHub Repo，上傳 README 說明客服 Agent 構想與使用場景 | 本 README | 完成 |
| 1 | 在 Coze 建立 Agent;查 Gemini 官網提供哪些模型;找出 Coze 最便宜的模型 | 小豆的模型、參數、Knowledge、Memory、Plugin、Guardrail 設定與測試 | 基本設定與測試完成，Temperature 對照實驗尚未做完 |
| 2 | 撰寫 System Prompt;完成 JSON 輸出測試;Prompt 存進 Coze prompt management | 在單元 1 的 Prompt 上小幅修改;獨立的 JSON 抽取 Agent;Injection 測試 | 進行中，測試結果待補 |
| 3 | 建立 variable(gender)，用戶說出性別時更新 | Coze Agent 的 user variable `gender` + Prompt 純文字更新規則；G1–G12 測試、輪數 3 對變數的對照實驗 | 實作與測試完成；能更新但不穩（G10 注入 3 次都被寫入、G11 四次裡兩次說已記錄卻沒寫入）；G13（跨對話保存）因不發布而未做 |
| 4 | 上傳課程列表為 Knowledge，Agent 回答課程問題時引用 | 待補 | 未開始 |
| 5 | 至少串接一個 browser Plugin，能爬取使用者給的課程網址 | 待補 | 未開始 |
| 6 | Chatflow:提取性別、職業、年齡、想上的課，並做意圖判斷 | 待補 | 未開始 |
| 7 | 進階 Chatflow:缺欄位就追問，欄位齊全才查 Knowledge | 待補 | 未開始 |
| 8 | Chatflow 最前端與最後端各加一個 LLM 當 Guardrail | 待補 | 未開始 |
| 9 | 部署到 Line，截圖 Coze 後台監控 | 待補 | 未開始 |
| 10 | 期末展示:功能、知識檢索準確度、防護、部署可用性 | 待補 | 未開始 |

## 安全與隱私

- 倉庫是公開的:**不放任何 API key、token、密碼與真實信箱**，`.gitignore` 已排除 `.env` 等檔案
- Gmail 外掛會用作者自己的信箱寄信，Agent 只在 Coze 內測試、**不發布**，測試時收件人只寄給作者自己
- 學習文件內的截圖只含 Coze 介面，已檢查不含信箱與金鑰

## 注意

- 單元 1 學習文件已更新為繳交的 Google 文件版本(不含老師留言，圖片以圖說呈現，截圖見 `docs/assets/unit1/`)
- 單元 2 文件與測試草稿仍是草稿，帶有【待補】標記處為尚未填入的實測結果，最終繳交版本以課程繳交的文件為準
- Prompt 屬於軟性限制，模型多半遵守但不保證;實際的注入測試結果見單元 2 文件
