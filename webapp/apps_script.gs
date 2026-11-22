/**
 * 期末練習網頁的寫入端（Google Apps Script）。貼在測試用 Google Sheet 的「擴充功能 → Apps Script」，
 * 部署成網頁應用程式（執行身分：我；存取權：所有人）。Streamlit 網頁把一列結果 POST 過來，這裡寫進「練習紀錄」分頁。
 *
 * 防濫用：網址本身要保密（放在 Streamlit secrets），另外要求一組通關碼 TOKEN，
 * 設在「專案設定 → 指令碼屬性」，名稱 TOKEN，值自己取一串亂碼；Streamlit secrets 填同一串。
 * 不需要服務帳戶，也不需要任何金鑰。
 */
const SHEET_NAME = '練習紀錄';
const MAX_COLS = 30;
const MAX_TEXT = 200;

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const expected = PropertiesService.getScriptProperties().getProperty('TOKEN');
    if (!expected || data.token !== expected) return reply({ ok: false, error: 'unauthorized' });
    if (!Array.isArray(data.row) || !Array.isArray(data.header) ||
        data.row.length !== data.header.length || data.row.length > MAX_COLS) {
      return reply({ ok: false, error: 'bad request' });
    }
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
    if (sheet.getLastRow() === 0) sheet.appendRow(data.header.map(clean));
    sheet.appendRow(data.row.map(clean));
    return reply({ ok: true });
  } catch (err) {
    return reply({ ok: false, error: 'exception' });
  }
}

// 文字以 = + - @ 開頭時加上 '，避免被當成公式；限制長度。數字原樣保留。
function clean(v) {
  if (typeof v === 'number') return v;
  let s = String(v == null ? '' : v).slice(0, MAX_TEXT);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
