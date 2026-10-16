# 單元 4 截圖說明

截圖都是 Coze 介面（Knowledge、Agent 編輯頁與預覽對話）與我自己畫的架構圖，取自 2026-10-14 與 2026-10-16/17 的實測。側欄含 Coze 顯示名稱，不含信箱或金鑰。

文件中的圖號（圖 1～14、圖 A）與檔名對照如下。

| 圖號 | 檔名 | 內容 | 對應章節 |
| --- | --- | --- | --- |
| 圖 A | fig09_rag-pipeline_error-points.png | RAG 流程與 K1–K10 的錯誤落點（我畫的） | 知識點、名詞關聯 |
| 圖 1 | fig01_creation-settings_auto-segment.jpg | Creation settings：預設 Automatic segmentation | 二 |
| 圖 2 | fig02_knowledge_8-segments.jpg | Knowledge 建立完成，8 segments | 二 |
| 圖 3 | fig03_knowledge-settings_defaults.jpg | Knowledge settings 預設值（Hybrid、5、0.50） | 二、四 |
| 圖 4 | fig04_knowledge-settings_rerank-source.jpg | Reranking、Reply、Show source | 二、四 |
| 圖 5 | fig05_k1_answer.jpg | K1 答對並帶引用標記 | 三 |
| 圖 6 | fig06_k1_sources.jpg | K1 撈到的段落卡片 | 三 |
| 圖 7 | fig07_k6_not-found.jpg | K6 撈到不相關段落，答「沒有」 | 三 |
| 圖 8 | fig08_k6b_keyword-found.jpg | K6b 補關鍵字後答對 | 三 |
| 圖 9 | fig10_k3_rerun_missed-unit8.jpg | K3 重跑仍漏單元 8 | 三 |
| 圖 10 | fig11_k4_not-in-list.jpg | K4 問不存在的單元 11 | 三 |
| 圖 11 | fig12_exp_semantics-threshold-0.20.jpg | 實驗複本：Semantics、門檻 0.20 的設定 | 後續實驗 |
| 圖 12 | fig13_exp_k6_semantics-0.20_found.jpg | 同一個 K6 在門檻 0.20 下答對 | 後續實驗 |
| 圖 13 | fig14_exp_fullprompt_k3_units678.jpg | 整份列表放進 Prompt，K3 答 6、7、8 | 後續實驗 |
| 圖 14 | fig15_exp_fullprompt_k6_answered.jpg | 整份列表放進 Prompt，K6 答出 | 後續實驗 |

檔名編號是我存檔的順序，和文件的圖號不同，以上表為準。
