"""期末練習網頁（Streamlit）：同學輸入假的帳戶摘要數字 → 驗算 → 顯示結果 → 寫一列到 Google Sheet。

計算與資料整理都在 logic.py（有單元測試）；這個檔只負責畫面與寫 Sheet。
本機沒有可用的 Streamlit（見 webapp/README.md），這個檔案沒有在本機跑過。
"""
import streamlit as st

import logic

st.set_page_config(page_title="保證金欄位驗算練習", page_icon="🧮")
st.title("保證金欄位驗算練習")
st.caption("中央大學 AI Agent 課期末專題「美股 IBKR 個人財務分析助理」的練習頁。")
st.warning("**請只輸入假的數字。**不要輸入真實帳戶的金額；你按下驗算後，輸入的數字會記錄到課程的 Google Sheet。")

st.markdown(
    "這一頁檢查幾個保證金欄位**彼此對不對得上**（依 IBKR 官方定義），並用簡化模型估算持倉同比例下跌多少時，"
    "超額流動性會降到 0。它只能說明欄位之間的關係，**不能證明任何券商的數字正確，也不是投資建議**。"
)

example = st.selectbox("帶入範例（都是假數字）", ["（自己填）"] + list(logic.EXAMPLES))
preset = logic.EXAMPLES.get(example, {})

with st.form("inputs"):
    raw = {}
    cols = st.columns(2)
    for i, (name, label, helptext) in enumerate(logic.FIELDS):
        default = "" if name not in preset else f"{preset[name]:,.0f}"
        raw[name] = cols[i % 2].text_input(label, value=default, help=helptext, key=f"{example}-{name}")
    nickname = st.text_input("暱稱（選填，不要填信箱或真名）", max_chars=logic.NICKNAME_MAX)
    submitted = st.form_submit_button("驗算")

if submitted:
    values, errors = logic.parse_inputs(raw)
    if errors:
        st.error("有欄位需要修正，沒有計算也沒有記錄：\n\n" + "\n".join("- " + e for e in errors))
    else:
        result = logic.run(values)
        for line in logic.summary_lines(result):
            st.write(line)
        st.caption("簡化模型：所有持倉同比例下跌、維持保證金與持倉市值成正比；不是券商的演算法，也不能預測會不會被強制平倉。")

        # 寫入走 Apps Script 網頁應用程式（webapp/apps_script.gs），不需要服務帳戶金鑰。
        try:
            cfg = st.secrets["sheet"]
            url, token = cfg["webapp_url"], cfg["token"]
        except Exception:
            cfg = None
        if not cfg:
            st.info("尚未設定 Google Sheet，這次沒有記錄。")
        else:
            try:
                import json
                import urllib.request

                body = json.dumps(logic.sheet_payload(values, result, nickname, token), ensure_ascii=False).encode("utf-8")
                req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    answer = json.loads(resp.read().decode("utf-8"))
                if answer.get("ok"):
                    st.success("已記錄到 Google Sheet。")
                else:
                    st.error(f"記錄到 Google Sheet 失敗：{answer.get('error', '未知原因')}")
            except Exception as exc:  # 寫不進去時不影響驗算結果，只提示
                st.error(f"記錄到 Google Sheet 失敗：{type(exc).__name__}")
