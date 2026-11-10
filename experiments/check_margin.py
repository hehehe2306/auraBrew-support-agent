"""稽查 IBKR 帳戶摘要的保證金欄位，數字彼此對不對得上。只讀、只算、不下單、不給買賣建議。

輸入：一個 JSON 檔，欄位名稱與 IBKR 連接器 get_account_summary 回傳的一致：
  net_liquidation, equity_with_loan_value, available_funds,
  initial_margin, maintenance_margin, excess_liquidity, buying_power
只用標準函式庫。真實帳戶資料不要放進 repo；測試只用假數字。

檢查的關係（來源：IBKR 官方定義，見 docs/drafts/IBKR學習方向綱要.md）：
  Available Funds  = ELV - Initial Margin
  Excess Liquidity = ELV - Maintenance Margin
  Buying Power     = Available Funds x 倍數（保證金帳戶 4 倍，依官方 FAQ；
                     官方詞彙表另有「取 ELV 與前一日 ELV 較小者」的版本，這裡無法驗證，
                     因為需要前一日 ELV，所以只在有提供 prev_day_elv 時才另外檢查）
Excess Liquidity < 0 時標示「可能被強制平倉」，這是描述官方定義，不是操作建議。
這個程式只能證明「欄位彼此對得上」，不能證明 IBKR 的保證金比例本身正確。

用法：
  python experiments/check_margin.py summary.json
發現對不上時結束碼為 1。
"""
import argparse
import json
import sys
from pathlib import Path

REQUIRED = [
    "net_liquidation", "equity_with_loan_value", "available_funds",
    "initial_margin", "maintenance_margin", "excess_liquidity", "buying_power",
]
TOLERANCE = 0.01  # 摘要是四捨五入到分，容許 1 分誤差
LEVERAGE = 4      # 保證金帳戶購買力倍數（官方 FAQ）


def close(a, b, tol=TOLERANCE):
    # 浮點誤差：差 1 分的兩個數相減可能得到 0.0100000000093，不能直接和 0.01 比（見測試）
    return abs(a - b) <= tol + 1e-6


def check(s, leverage=LEVERAGE):
    """回傳問題清單；空清單代表欄位彼此一致。"""
    missing = [k for k in REQUIRED if k not in s]
    if missing:
        return [f"[缺欄位] {', '.join(missing)}"]

    problems = []
    elv = s["equity_with_loan_value"]

    want = elv - s["initial_margin"]
    if not close(s["available_funds"], want):
        problems.append(f"[可用資金] available_funds={s['available_funds']}，"
                        f"但 ELV - 初始保證金 = {want:.2f}")

    want = elv - s["maintenance_margin"]
    if not close(s["excess_liquidity"], want):
        problems.append(f"[超額流動性] excess_liquidity={s['excess_liquidity']}，"
                        f"但 ELV - 維持保證金 = {want:.2f}")

    # 可用資金本身有 ±0.5 分的四捨五入，乘上倍數後誤差也跟著放大
    want = s["available_funds"] * leverage
    if not close(s["buying_power"], want, TOLERANCE * leverage):
        problems.append(f"[購買力] buying_power={s['buying_power']}，"
                        f"但 可用資金 x {leverage} = {want:.2f}")

    if "prev_day_elv" in s:
        alt = (min(elv, s["prev_day_elv"]) - s["initial_margin"]) * leverage
        if not close(s["buying_power"], alt, TOLERANCE * leverage):
            problems.append(f"[購買力·詞彙表版] 取 min(ELV, 前日 ELV) 算出 {alt:.2f}，"
                            f"與 buying_power={s['buying_power']} 不同")
    return problems


def warnings(s):
    """不算錯誤的觀察。目前只有超額流動性為負。"""
    out = []
    if s.get("excess_liquidity", 0) < 0:
        out.append("excess_liquidity < 0：依官方定義，這代表低於維持保證金，帳戶可能被強制平倉。")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("summary", help="帳戶摘要 JSON 檔")
    ap.add_argument("--leverage", type=float, default=LEVERAGE, help="購買力倍數，預設 4")
    a = ap.parse_args(argv)

    s = json.loads(Path(a.summary).read_text(encoding="utf-8"))
    for w in warnings(s):
        print("注意：", w)
    problems = check(s, a.leverage)
    if problems:
        print("\n".join(problems))
        return 1
    print("OK：可用資金、超額流動性、購買力與官方定義對得上。")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
