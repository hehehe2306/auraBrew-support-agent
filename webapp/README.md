# 期末練習網頁（b＋B：練習型＋Streamlit Community Cloud）

使用者 2026-11-23 決定的方向：同學輸入**假的**帳戶摘要數字，網頁用 `experiments/` 裡已經有單元測試的驗算算出結果，再寫一列到 Google Sheet。不碰真實帳戶、不呼叫模型、不給投資建議。選項比較見 `docs/drafts/期末網頁與GoogleSheet_選項.md`。

## 檔案

| 檔案 | 內容 | 驗證狀態 |
| :- | :- | :- |
| `logic.py` | 欄位定義、三組假數字範例、輸入檢查、呼叫驗算、組 Sheet 那一列；只用標準函式庫 | 單元測試 `test_logic.py` |
| `app.py` | Streamlit 畫面與寫 Sheet | **本機沒跑過**（原因見下） |
| `requirements.txt` | Streamlit Cloud 安裝用：`streamlit`、`gspread`、`google-auth`（沒有鎖版本） | — |

## 為什麼本機沒跑過

這台電腦能用的 Python 是 python.org 的免安裝版，沒有 pip；uv 的 Python 被 Windows 智慧型應用程式控制擋下（2026-11-22 查證）。Streamlit 的相依套件也含未簽章的元件，**推論**在本機同樣會被擋，沒有實測。所以畫面要部署到 Streamlit Community Cloud 才看得到。

## 部署步驟（要你本人做；建立帳號、金鑰、分享權限都不由 Agent 代做）

1. **建立測試用 Sheet**：先用你自己的一份空白 Google Sheet，分頁命名為 `練習紀錄`。老師的 Sheet 等權限確認後再換。
2. **建立服務帳戶**：在 Google Cloud Console 建一個專案、啟用 Google Sheets API、建立服務帳戶並下載 JSON 金鑰。**這把金鑰不能 commit、不能貼進任何公開的地方。**
3. **把 Sheet 分享給服務帳戶**：用 JSON 裡的 `client_email`，給「編輯者」權限。
4. **部署**：在 Streamlit Community Cloud 用 GitHub 登入，選這個 repo、分支 `main`、入口檔 `webapp/app.py`。
5. **設定 secrets**（在 Streamlit 的 app 設定裡貼，不放進 repo）：

   ```toml
   [sheet]
   key = "試算表網址中 /d/ 和 /edit 之間那段 ID"
   worksheet = "練習紀錄"

   [gcp_service_account]
   type = "service_account"
   # 其餘欄位照 JSON 金鑰逐項填入
   ```

6. 打開網頁，用三組範例各按一次「驗算」，確認 Sheet 多了 3 列且第一列是標題。

沒有設定 secrets 時，網頁照樣能驗算，只是會顯示「尚未設定 Google Sheet，這次沒有記錄」。

## 已知限制

- 程式無法分辨使用者輸入的是不是真實帳戶數字；只能在頁面上提醒。
- 暱稱選填，含 `@` 的一律不記錄，最長 20 字。
- 網址公開，任何人都能送資料；目前沒有防濫用機制。
- Streamlit Community Cloud 12 小時沒有流量會睡著（官方文件的搜尋摘要，未逐頁讀）。
- `requirements.txt` 沒有鎖版本，部署時會裝當時的最新版。
