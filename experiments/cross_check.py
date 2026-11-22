"""兩個獨立算法互相稽查：本 repo 的 Python 驗算（check_margin、stress_margin）與 ibkr-agent 的 skill 流程
（account-health、liquidity-stress，由 LLM 照步驟執行）對同一個帳戶算出的比例，逐項比對。只讀、只算、不下單。

兩個子命令：
  export  讀帳戶摘要 JSON，用 check_margin 與 stress_margin 算出**只有比例與通過／不通過**的 JSON（不含金額），
          給 06:30 的驗算排程存到 data/margin_reports/（已被 .gitignore 排除）。
  compare 讀上面那份 JSON 與 ibkr-agent 的 *-metrics.json、*-stress.json，輸出比對表（Markdown）。

比對項目與容許差（**容許差是暫定值，由使用者決定**；理由見各項註解）：
  槓桿             0.01   帳戶回報的 leverage 只到小數 2 位
  保證金緩衝（%）   0.05   兩邊都由欄位算出，只差四捨五入；但兩個排程取資料的時間不同
  破線距離（%）     0.10   同上，分母 V − MM 放大誤差
  超額流動性一致性  布林   兩邊對「超額流動性 是否等於 ELV − 維持保證金」的判斷要相同

限制（寫文件時不要說成「證明正確」）：
  - 兩邊一致只代表兩種實作算出同樣的數字，不能證明公式或 IBKR 的數字正確。
  - 兩個排程取資料的時間不同（06:30 與 07:30）；收盤後數字通常不變，但不保證。
  - 不一致時只列出差額，不猜哪邊錯、也不猜原因。

只用標準函式庫。
"""
import argparse
import json
import sys
from pathlib import Path

try:  # 以模組執行（python -m experiments.cross_check）或直接執行腳本都能用
    from experiments import check_margin, stress_margin
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from experiments import check_margin, stress_margin

TOLERANCES = {"leverage": 0.01, "cushion_pct": 0.05, "d_star_pct": 0.10}  # 暫定，見檔頭說明
EL_GAP_TOL = 0.01


def _pct(x):
    return None if x is None else round(x * 100, 4)


def export(summary, date):
    """帳戶摘要 → 只有比例與布林的 dict（不含任何金額）。"""
    problems = check_margin.check(summary)
    missing = [p for p in problems if p.startswith("[缺欄位]")]
    tags = {"available_funds": "[可用資金]", "excess_liquidity": "[超額流動性]", "buying_power": "[購買力]"}
    checks = None if missing else {k: not any(p.startswith(t) for p in problems) for k, t in tags.items()}

    r = stress_margin.assess(summary)
    if "error" in r:
        lev = cus = d = None
        note = r["error"]
    else:
        lev, cus, d, note = r["leverage"], r["cushion"], r["drop_to_zero"], r["drop_note"]
    v = summary.get("gross_position_value")
    mm = summary.get("maintenance_margin")
    mm_ratio = (mm / v * 100) if (v and mm is not None and v > 0) else None
    return {
        "schema": 1,
        "date": date,
        "source": "auraBrew experiments/check_margin.py + stress_margin.py",
        "checks": checks,
        "leverage": None if lev is None else round(lev, 4),
        "cushion_pct": _pct(cus),
        "d_star_pct": _pct(d),
        "d_star_note": note or None,
        "mm_to_position_pct": None if mm_ratio is None else round(mm_ratio, 4),
    }


def _row(name, a, b, tol):
    if a is None or b is None:
        return (name, a, b, None, "未取得")
    diff = round(float(a) - float(b), 4)
    return (name, a, b, diff, "一致" if abs(diff) <= tol + 1e-9 else "不一致")


def compare(audit, metrics, stress=None, tol=None):
    """回傳 (rows, notes)。rows：(項目, Python 驗算, skill 流程, 差, 結果)。"""
    tol = dict(TOLERANCES, **(tol or {}))
    notes = []
    if audit.get("date") != metrics.get("date"):
        notes.append(f"日期不同：Python 驗算 {audit.get('date')}、skill 流程 {metrics.get('date')}；仍照比，但結果可能只是時間差。")

    rows = [
        _row("槓桿（Python V/NLV 對 帳戶回報 leverage）", audit.get("leverage"), metrics.get("leverage"), tol["leverage"]),
        _row("保證金緩衝 %（超額流動性 ÷ 淨值）", audit.get("cushion_pct"), metrics.get("cushion_primary_pct"), tol["cushion_pct"]),
    ]
    d_skill = None if stress is None else stress.get("d_star_el_pct")
    if stress is None:
        notes.append("沒有 skill 流程的 stress.json，破線距離不比對。")
    rows.append(_row("破線距離 %（以超額流動性為基準）", audit.get("d_star_pct"), d_skill, tol["d_star_pct"]))

    checks = audit.get("checks") or {}
    el_ok_py = checks.get("excess_liquidity")
    gap = metrics.get("el_gap")
    el_ok_skill = None if gap is None else abs(float(gap)) <= EL_GAP_TOL + 1e-9
    if el_ok_py is None or el_ok_skill is None:
        rows.append(("超額流動性 = ELV − 維持保證金？", el_ok_py, el_ok_skill, None, "未取得"))
    else:
        rows.append(("超額流動性 = ELV − 維持保證金？", el_ok_py, el_ok_skill, None,
                     "一致" if el_ok_py == el_ok_skill else "不一致"))
    return rows, notes


def _fmt(x):
    if x is None:
        return "未取得"
    if isinstance(x, bool):
        return "是" if x else "否"
    return f"{x}"


def render(rows, notes, sources):
    lines = ["# 兩個獨立算法互相稽查", "", "來源：" + "；".join(sources), "",
             "| 項目 | Python 驗算 | skill 流程 | 差 | 結果 |", "| :- | :- | :- | :- | :- |"]
    for name, a, b, diff, res in rows:
        lines.append(f"| {name} | {_fmt(a)} | {_fmt(b)} | {'—' if diff is None else diff} | {res} |")
    lines += ["", f"容許差（暫定，由使用者決定）：槓桿 {TOLERANCES['leverage']}、緩衝 {TOLERANCES['cushion_pct']} 個百分點、"
              f"破線距離 {TOLERANCES['d_star_pct']} 個百分點。"]
    for n in notes:
        lines.append(f"- {n}")
    lines += ["- 兩邊一致只代表兩種實作算出同樣的數字，不能證明公式或 IBKR 的數字正確；不一致時只列差額，不猜哪邊錯。",
              "- 本表只比對計算，不判斷帳戶好壞，也不給任何操作建議。"]
    return "\n".join(lines) + "\n"


def _load(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("summary")
    e.add_argument("--date", required=True)
    e.add_argument("--out", required=True)
    c = sub.add_parser("compare")
    c.add_argument("--audit", required=True)
    c.add_argument("--metrics", required=True)
    c.add_argument("--stress")
    c.add_argument("--out")
    a = ap.parse_args(argv)

    if a.cmd == "export":
        data = export(_load(a.summary), a.date)
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(data, ensure_ascii=False))
        return 0

    missing = [p for p in (a.audit, a.metrics) if not Path(p).exists()]
    if missing:
        text = "# 兩個獨立算法互相稽查\n\n未比對：找不到 " + "、".join(missing) + "。\n"
    else:
        stress = _load(a.stress) if a.stress and Path(a.stress).exists() else None
        rows, notes = compare(_load(a.audit), _load(a.metrics), stress)
        text = render(rows, notes, [a.audit, a.metrics] + ([a.stress] if stress else []))
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
