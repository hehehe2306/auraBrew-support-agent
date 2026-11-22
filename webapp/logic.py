"""期末練習網頁的邏輯層：同學輸入「假的」帳戶摘要數字，用 experiments/ 裡已經有單元測試的驗算算出結果，
再組成要寫進 Google Sheet 的一列。只用標準函式庫，所以能在沒有 Streamlit 的環境做單元測試。

不讀任何真實帳戶、不呼叫模型、不給投資建議。網頁上會提醒使用者只輸入假數字；程式無法分辨數字真假。
"""
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments import check_margin, stress_margin  # noqa: E402

# (欄位名, 中文標籤, 說明) —— 欄位名與 IBKR 連接器 get_account_summary 一致
FIELDS = [
    ("net_liquidation", "淨值（NLV）", "帳戶全部清算後的價值"),
    ("equity_with_loan_value", "含貸款價值資產（ELV）", "可拿來計算保證金的資產"),
    ("initial_margin", "初始保證金", "開新部位需要的保證金"),
    ("maintenance_margin", "維持保證金", "持有部位需要維持的保證金"),
    ("available_funds", "可用資金", "官方定義：ELV − 初始保證金"),
    ("excess_liquidity", "超額流動性", "官方定義：ELV − 維持保證金；低於 0 可能被強制平倉"),
    ("buying_power", "購買力", "保證金帳戶：可用資金 × 4"),
    ("gross_position_value", "持倉總市值", "所有持倉的市值合計"),
]
FIELD_NAMES = [f[0] for f in FIELDS]

# 三組範例（全部是假數字，彼此關係手算過，見 test_logic.py）
EXAMPLES = {
    "全部對得上": dict(net_liquidation=100000, equity_with_loan_value=100000, initial_margin=45000,
                   maintenance_margin=37500, available_funds=55000, excess_liquidity=62500,
                   buying_power=220000, gross_position_value=150000),
    "超額流動性對不上": dict(net_liquidation=100000, equity_with_loan_value=100000, initial_margin=45000,
                      maintenance_margin=37500, available_funds=55000, excess_liquidity=63000,
                      buying_power=220000, gross_position_value=150000),
    "離破線很近": dict(net_liquidation=100000, equity_with_loan_value=100000, initial_margin=90000,
                   maintenance_margin=85000, available_funds=10000, excess_liquidity=15000,
                   buying_power=40000, gross_position_value=300000),
}

NICKNAME_MAX = 20
TAIPEI = timezone(timedelta(hours=8))


def parse_inputs(raw):
    """raw：{欄位名: 字串或數字}。回傳 (數字 dict, 錯誤清單)。空白、非數字都列成錯誤，不補值。"""
    values, errors = {}, []
    for name, label, _ in FIELDS:
        v = raw.get(name)
        if v is None or (isinstance(v, str) and v.strip() == ""):
            errors.append(f"{label}：未填")
            continue
        try:
            values[name] = float(str(v).replace(",", "").strip())
        except ValueError:
            errors.append(f"{label}：不是數字（{v}）")
    return values, errors


def run(values):
    """用 experiments/ 的驗算算出結果。values 必須包含全部欄位（先過 parse_inputs）。"""
    problems = check_margin.check(values)
    r = stress_margin.assess(values)
    return {
        "problems": problems,
        "warnings": check_margin.warnings(values),
        "leverage": r.get("leverage"),
        "cushion": r.get("cushion"),
        "drop_to_zero": r.get("drop_to_zero"),
        "drop_note": r.get("drop_note", ""),
    }


def summary_lines(result):
    """給網頁顯示的白話結果（不判斷好壞、不給建議）。"""
    out = []
    if result["problems"]:
        out.append("欄位檢查：有對不上的地方")
        out += ["・" + p for p in result["problems"]]
    else:
        out.append("欄位檢查：可用資金、超額流動性、購買力都和官方定義對得上")
    out += ["注意：" + w for w in result["warnings"]]
    lev, cus, d = result["leverage"], result["cushion"], result["drop_to_zero"]
    out.append("槓桿（持倉總市值 ÷ 淨值）：" + ("無法計算" if lev is None else f"{lev:.2f}"))
    out.append("保證金緩衝（超額流動性 ÷ 淨值）：" + ("無法計算" if cus is None else f"{cus:.1%}"))
    if d is None:
        out.append(f"持倉同比例下跌多少，超額流動性會降到 0：不適用（{result['drop_note']}）")
    else:
        out.append(f"持倉同比例下跌多少，超額流動性會降到 0（簡化模型的粗估）：{d:.1%}")
    return out


def clean_nickname(nickname):
    """暱稱選填：去頭尾空白、限制長度；不收信箱（含 @ 的一律清空）。"""
    n = (nickname or "").strip()
    if "@" in n:
        return ""
    return n[:NICKNAME_MAX]


SHEET_HEADER = (["時間（台北）", "暱稱"] + [label for _, label, _ in FIELDS]
                + ["欄位檢查", "對不上的項目", "槓桿", "緩衝%", "破線距離%"])


def sheet_row(values, result, nickname="", now=None):
    """組成寫進 Sheet 的一列，欄位順序與 SHEET_HEADER 相同。"""
    now = now or datetime.now(TAIPEI)
    failed = [p.split("]")[0].lstrip("[") for p in result["problems"]]
    lev, cus, d = result["leverage"], result["cushion"], result["drop_to_zero"]
    return ([now.strftime("%Y-%m-%d %H:%M:%S"), clean_nickname(nickname)]
            + [values[n] for n in FIELD_NAMES]
            + ["通過" if not failed else "不通過", "、".join(failed),
               "" if lev is None else round(lev, 4),
               "" if cus is None else round(cus * 100, 2),
               "" if d is None else round(d * 100, 2)])


def sheet_payload(values, result, nickname, token, now=None):
    """送給 Apps Script（webapp/apps_script.gs）的 JSON 內容：通關碼、標題列、資料列。"""
    return {"token": token, "header": SHEET_HEADER, "row": sheet_row(values, result, nickname, now)}
