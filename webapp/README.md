# 期末練習網頁（b＋B：練習型＋Streamlit Community Cloud）

使用者 2026-11-23 決定的方向：同學輸入**假的**帳戶摘要數字，網頁用 `experiments/` 裡已經有單元測試的驗算算出結果，再寫一列到 Google Sheet。不碰真實帳戶、不呼叫模型、不給投資建議。選項比較見 `docs/drafts/期末網頁與GoogleSheet_選項.md`。

## 檔案

| 檔案 | 內容 | 驗證狀態 |
| :- | :- | :- |
| `logic.py` | 欄位定義、三組假數字範例、輸入檢查、呼叫驗算、組 Sheet 那一列；只用標準函式庫 | 單元測試 `test_logic.py` |
| `app.py` | Streamlit 畫面與寫 Sheet | 本機沒跑過（原因見下）；**2026-11-23 部署到 Streamlit Cloud 後實測**：三組範例各送一次，測試 Sheet 寫入 3 列＋標題，數字與手算一致（含「不通過／超額流動性」那條路） |
| `apps_script.gs` | 貼在 Sheet 的 Apps Script，接收網頁送來的一列並寫入；檢查通關碼、欄位數、把 = + - @ 開頭的文字加 ' 避免變成公式 | 2026-11-23 部署後實測：自動建立「練習紀錄」分頁、寫入標題與 3 列。**通關碼錯誤、格式錯誤、公式開頭文字的處理沒有實測** |
| `requirements.txt` | Streamlit Cloud 安裝用：只有 `streamlit`（沒有鎖版本） | — |

## 為什麼本機沒跑過

這台電腦能用的 Python 是 python.org 的免安裝版，沒有 pip；uv 的 Python 被 Windows 智慧型應用程式控制擋下（2026-11-22 查證）。Streamlit 的相依套件也含未簽章的元件，**推論**在本機同樣會被擋，沒有實測。所以畫面要部署到 Streamlit Community Cloud 才看得到。

## 部署步驟（要你本人做；帳號、網址、通關碼都不由 Agent 代做）

寫入 Sheet 改用 **Apps Script**（2026-11-23）：原本的服務帳戶做法在使用者的 Google Cloud 專案出現「服務帳戶金鑰建立功能已停用」，所以改成不需要金鑰的方式。

1. **建立測試用 Sheet**：用你自己的帳號開一份空白 Google Sheet（分頁不用先建，第一次寫入時會自動建「練習紀錄」）。老師的 Sheet 等權限確認後再換。
2. **貼上寫入程式**：在那份 Sheet 點「擴充功能 → Apps Script」，把 `webapp/apps_script.gs` 的內容整段貼上，取代原本的內容，存檔。
3. **設通關碼**：在 Apps Script 左邊「專案設定」（齒輪）→「指令碼屬性」→ 新增屬性，名稱 `TOKEN`，值自己取一串 20 字以上的亂碼。**不要 commit、不要貼到公開的地方。**
4. **部署**：右上「部署 → 新增部署作業」，類型選「網頁應用程式」，「執行身分」選**我**，「誰可以存取」選**所有人**。第一次會要你授權存取自己的試算表，照畫面同意。部署完複製「網頁應用程式網址」（以 `/exec` 結尾）。**這個網址也要保密。**
5. **部署 Streamlit**：在 share.streamlit.io 用 GitHub 登入，選這個 repo、分支 `main`、入口檔 `webapp/app.py`。在 Advanced settings 的 Secrets 貼：

   ```toml
   [sheet]
   webapp_url = "第 4 步複製的 /exec 網址"
   token = "第 3 步的通關碼"
   ```

6. 打開網頁，用三組範例各按一次「驗算」，確認 Sheet 出現「練習紀錄」分頁、第一列是標題、下面多 3 列。

沒有設定 secrets 時，網頁照樣能驗算，只是會顯示「尚未設定 Google Sheet，這次沒有記錄」。之後若修改 Apps Script，要用「管理部署作業 → 編輯 → 新版本」重新部署，網址才會用到新程式。

## 已知限制

- 程式無法分辨使用者輸入的是不是真實帳戶數字；只能在頁面上提醒。
- 暱稱選填，含 `@` 的一律不記錄，最長 20 字。
- Streamlit 網頁的網址是公開的，任何人都能按「驗算」送一列進 Sheet；Apps Script 網址與通關碼放在 secrets 裡，只防止有人繞過網頁直接寫入。
- Streamlit Community Cloud 12 小時沒有流量會睡著（官方文件的搜尋摘要，未逐頁讀）。
- `requirements.txt` 沒有鎖版本，部署時會裝當時的最新版。
