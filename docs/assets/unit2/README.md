# 單元 2 截圖說明

2026-10-01 在 Coze 測試「客人沒給信箱就說已完成付款」的畫面。Prompt 為 v2(見 `prompts/customer_service_system_prompt.md`)，輸入皆為「我已完成付款」。截圖已確認不含信箱地址。

| 檔案 | 內容 | 備註 |
| --- | --- | --- |
| fig01_prompt-v2_test0.1.png | 測試0.1 套用 v2 Prompt 後的設定畫面 | Temperature 0.1，上下文輪數 8，長度 1024 |
| fig02_prompt-v2_test0.3.png | 測試0.3 套用 v2 Prompt 後的設定畫面 | Temperature 0.3，上下文輪數 8，長度 1024 |
| fig03_nomail_test0.1_run1_asks-email.png | 測試0.1 第 1 次:直接詢問信箱 | 2192 tokens |
| fig04_nomail_test0.3_asks-email_unauthorized-badge.png | 測試0.3 詢問信箱;Gmail 外掛旁有「1 Unauthorized」標籤 | 這張的執行流程未展開，看不出有沒有呼叫外掛 |
| fig05_nomail_test0.1_run2_no-gmail-call.png | 測試0.1 第 2 次:流程只有 Knowledge searched，沒有 Used Gmail | 2177 tokens |
| fig06_nomail_test0.3_gmail-to-empty_rpcerror.png | 測試0.3:呼叫 Gmail.sendMessage，`to` 為空，外掛回傳 RPCError(The domain is forbidden to access)，之後才詢問信箱 | 沒有信寄出(Gmail 已傳送無紀錄) |
| fig07_nomail_test0.1_run3_no-gmail-call.png | 測試0.1 第 3 次:沒有 Used Gmail | 929 tokens |
| fig08_nomail_test0.3_run3_used-gmail_rounds3.png | 測試0.3:呼叫 Gmail 後才詢問信箱 | **上下文輪數被誤改成 3**(0.1 為 8)，不可與 0.1 直接比較;之後已改回 8 並清空歷史重測，見 fig09 到 fig12 |
| fig09_nomail_cleared_test0.1_run1_no-gmail-call.png | 清空歷史後，測試0.1 第 1 次:沒有 Used Gmail，先問信箱 | 輪數 8，930 tokens;此時兩個 Agent 的 Gmail 都顯示 1 Unauthorized |
| fig10_nomail_cleared_test0.3_run1_no-gmail-call.png | 清空歷史後，測試0.3 第 1 次:沒有 Used Gmail，先問信箱 | 輪數 8，930 tokens |
| fig11_nomail_cleared_test0.1_run2-3_same-conversation.png | 測試0.1 第 2、3 次，**接在同一個對話裡**:都沒有 Used Gmail | 第 3 次回覆有「還是需要…」，可見模型看得到上一輪，兩次不是獨立樣本 |
| fig12_nomail_cleared_test0.3_run2-3_same-conversation.png | 測試0.3 第 2、3 次，**接在同一個對話裡**:都沒有 Used Gmail | 同上，不是獨立樣本 |

判讀與限制見 `docs/drafts/第三週學習文件_單元2.md` 第五章。
