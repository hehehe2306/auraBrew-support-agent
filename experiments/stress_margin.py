"""壓力測試與槓桿評估：帳戶摘要的數字，在持倉下跌時會怎麼變。只讀、只算、不下單、不給買賣建議。

輸入：與 check_margin.py 相同的 JSON（欄位名稱同 IBKR 連接器 get_account_summary），另需
  gross_position_value。可選 leverage（帳戶自己回報的槓桿，用來對照下面的算法）。
只用標準函式庫。真實帳戶資料不要放進 repo；測試只用假數字。

模型（都是我的簡化假設，不是 IBKR 的演算法）：
  1. 所有持倉都是多頭，價格同比例下跌 d，現金不變：ELV(d) = ELV - d * V
  2. 維持保證金與持倉市值成正比：MM(d) = MM * (1 - d)
  3. 所以 Excess Liquidity(d) = EL - d * (V - MM)，變成 0 的跌幅 d* = EL / (V - MM)
  其中 V = gross_position_value。
  限制：有空頭、選擇權、期貨或多幣別時假設不成立；個股實際維持保證金會隨價格與規則調整。
  所以 d* 只是「在這些假設下的粗估」，不能當作會不會被強制平倉的預測。

槓桿 = V / net_liquidation（我的定義，用帳戶回報的 leverage 對照；兩者差太多就標出來）。
「安不安全」的門檻要由人決定，這個程式只輸出數字，不下判斷。

用法：
  python experiments/stress_margin.py summary.json
"""
import argparse
import json
import sys
from pathlib import Path

REQUIRED = ["net_liquidation", "equity_with_loan_value", "maintenance_margin",
            "excess_liquidity", "gross_position_value"]
LEVERAGE_TOL = 0.05  # 帳戶回報的 leverage 只有一兩位小數


def leverage(s):
    """V / NLV。NLV <= 0 時沒有意義，回 None。"""
    if s["net_liquidation"] <= 0:
        return None
    return s["gross_position_value"] / s["net_liquidation"]


def cushion(s):
    """保證金緩衝（margin cushion）：超額流動性 / 淨清算值，採 IBKR FAQ「What is my Margin Cushion?」的定義
    （https://www.interactivebrokers.com/support/faq/content/margin-cushion-34494478，查詢日 2026-11-22）。
    NLV <= 0 回 None。"""
    nlv = s["net_liquidation"]
    return s["excess_liquidity"] / nlv if nlv > 0 else None


def drop_to_zero_excess(s):
    """持倉同比例下跌多少，超額流動性會降到 0。

    回傳 (跌幅, 說明)：跌幅為 0~1 的小數，或 None（模型不適用）。
    """
    v = s["gross_position_value"]
    mm = s["maintenance_margin"]
    el = s["excess_liquidity"]
    if v <= 0:
        return None, "沒有持倉，沒有可下跌的部位"
    if v <= mm:
        return None, "維持保證金不小於持倉市值，這個簡化模型不適用"
    if el <= 0:
        return 0.0, "超額流動性已經 <= 0"
    d = el / (v - mm)
    if d >= 1:
        return None, "即使持倉跌到 0，超額流動性仍為正（相當於跌幅 >= 100%）"
    return d, ""


def excess_after_drop(s, d):
    """在上述假設下，持倉跌 d 後的超額流動性（用來交叉驗證 drop_to_zero_excess）。"""
    return s["excess_liquidity"] - d * (s["gross_position_value"] - s["maintenance_margin"])


def assess(s):
    missing = [k for k in REQUIRED if k not in s]
    if missing:
        return {"error": f"缺欄位：{', '.join(missing)}"}
    lev = leverage(s)
    d, why = drop_to_zero_excess(s)
    notes = []
    if lev is not None and "leverage" in s:
        reported = float(s["leverage"])
        if abs(reported - lev) > LEVERAGE_TOL:
            notes.append(f"帳戶回報槓桿 {reported}，但 持倉市值/淨清算值 = {lev:.2f}，我的定義可能不對")
    return {"leverage": lev, "cushion": cushion(s), "drop_to_zero": d,
            "drop_note": why, "notes": notes}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("summary", help="帳戶摘要 JSON 檔")
    a = ap.parse_args(argv)
    s = json.loads(Path(a.summary).read_text(encoding="utf-8"))
    r = assess(s)
    if "error" in r:
        print(r["error"])
        return 2
    lev = "無法計算" if r["leverage"] is None else f"{r['leverage']:.2f}"
    cus = "無法計算" if r["cushion"] is None else f"{r['cushion']:.1%}"
    print(f"槓桿（持倉市值/淨清算值）：{lev}")
    print(f"保證金緩衝（超額流動性/淨清算值）：{cus}")
    if r["drop_to_zero"] is None:
        print(f"超額流動性降到 0 的跌幅：不適用（{r['drop_note']}）")
    else:
        print(f"超額流動性降到 0 的跌幅（粗估）：{r['drop_to_zero']:.1%}"
              + (f"（{r['drop_note']}）" if r["drop_note"] else ""))
    for n in r["notes"]:
        print("注意：", n)
    print("門檻（多低算不安全）由人決定，這裡不下判斷。")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
