"""驗算 AuraBrew 手冊與事實表是否一致，並找出改了某個事實後要跟著改的地方。

事實表：knowledge/aurabrew_facts.json（唯一來源）
只用標準函式庫，不需要安裝任何套件。

用法：
  python experiments/check_facts.py                      檢查目前手冊
  python experiments/check_facts.py --set x1_price=5280  假設改了價格，看手冊哪裡會對不上（不改檔案）
  python experiments/check_facts.py --changed x1_price   列出改這個事實要跟著檢查的文件
發現不一致時結束碼為 1。
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FACTS = ROOT / "knowledge" / "aurabrew_facts.json"


def load(path=FACTS):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def show(v):
    """整數加千分位，其餘（字串）照原樣，用來填進 manual_snippet。"""
    return f"{v:,}" if isinstance(v, int) else str(v)


def values(data, overrides=None):
    vals = {k: f["value"] for k, f in data["facts"].items()}
    vals.update(overrides or {})
    return vals


def compute_derived(data, vals):
    out = {}
    for name, d in data["derived"].items():
        out[name] = sum(vals[k] * sign for k, sign in d["terms"])
    return out


def check(data, manual_text, overrides=None):
    """回傳問題清單；空清單代表手冊與事實表一致。"""
    problems = []
    vals = values(data, overrides)
    for key, fact in data["facts"].items():
        want = fact["manual_snippet"].format(v=show(vals[key]))
        if want not in manual_text:
            problems.append(f"[事實] {key} = {show(vals[key])}：手冊裡找不到「{want}」")
    for name, d in data["derived"].items():
        computed = compute_derived(data, vals)[name]
        m = re.search(d["stated_pattern"], manual_text)
        if not m:
            problems.append(f"[衍生] {name}：手冊裡找不到數字（pattern {d['stated_pattern']}）")
            continue
        stated = int(m.group(1).replace(",", ""))
        if stated != computed:
            problems.append(f"[衍生] {name}：手冊寫 {stated}，用事實表算出來是 {computed}")
    return problems


def affected(data, key):
    """改了事實 key，要跟著檢查哪些衍生數字與文件。"""
    docs = list(data["facts"][key]["referenced_by"])
    for name, d in data["derived"].items():
        if any(k == key for k, _ in d["terms"]):
            docs.append(f"（衍生數字 {name} 會變）")
            docs.extend(d["referenced_by"])
    return docs


def parse_overrides(items):
    out = {}
    for s in items or []:
        k, _, raw = s.partition("=")
        out[k] = int(raw) if raw.isdigit() else raw
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", nargs="*", help="假設改值，例如 x1_price=5280（不改檔案）")
    ap.add_argument("--changed", help="列出改這個事實要跟著檢查的文件")
    a = ap.parse_args(argv)

    data = load()
    if a.changed:
        if a.changed not in data["facts"]:
            print(f"沒有這個事實：{a.changed}（可用：{', '.join(data['facts'])}）")
            return 2
        for line in affected(data, a.changed):
            print("-", line)
        return 0

    manual = (ROOT / data["manual_file"]).read_text(encoding="utf-8")
    problems = check(data, manual, parse_overrides(a.set))
    if problems:
        print("\n".join(problems))
        return 1
    print("OK：手冊與事實表一致，衍生數字也對得上。")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
