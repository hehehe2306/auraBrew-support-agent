"""外匯餘額保證金驗算：照 IBKR 知識庫「Currency margin calculation」的做法算一遍。只讀、只算、不下單、不給買賣建議。

來源（2026-11-19 用瀏覽器讀過原文）：
  https://www.interactivebrokers.com/support/faq/content/currency-margin-calculation-1163245559
  https://www.interactivebrokers.com/support/faq/content/there-margin-calculation-fx-balances-41560254

做法（官方範例的步驟）：
  1. 各幣別淨清算值換算成基準貨幣（base-currency equivalent）。
  2. 每個貨幣對有一個折減率（haircut）。
  3. 找出負的餘額；用折減率最低的正餘額去抵銷它，抵銷的那一段乘以折減率，就是這一段的保證金。
  4. 重複直到所有負餘額都被抵銷；各段保證金相加。

限制（寫文件時不要說成「證明 IBKR 算對」）：
  - 只驗證「官方範例」那一種情況（一個負餘額、兩個正餘額）。多個負餘額時，我的處理方式是
    「最大的負餘額先抵銷」，這是我的解讀，官方範例沒有講；測試 test_two_negatives_* 只是在鎖住我自己的規則。
  - 折減率必須來自我的帳戶所屬的 IBKR 實體與規則。官方範例的 0.025、0.10 是示範數字，
    IB Canada 的比例表也不能直接當作我的帳戶適用的數字。本程式不內建任何折減率，由呼叫者給。
  - 沒有實作：提款版（KB971）、「取 KB970 與現金外匯部位保證金兩者較大者」（只在搜尋摘要看過，沒讀到原文）。
  - 負餘額找不到足夠的正餘額抵銷時，不編造折減率，回報 uncovered 讓人處理。

只用標準函式庫。真實帳戶資料不要放進 repo；測試只用假數字與官方範例的示範數字。
"""

EPS = 1e-9


def to_base(local_amount, units_per_base):
    """把外幣淨清算值換成基準貨幣等值。units_per_base = 1 單位基準貨幣等於幾單位該外幣。

    官方範例：EUR USD 0.72860 表示 1 USD = 0.72860 EUR；KRW 1330 表示 1 USD = 1330 KRW。
    """
    if units_per_base <= 0:
        raise ValueError("units_per_base 必須 > 0")
    return local_amount / units_per_base


def _haircut(haircuts, a, b):
    """haircuts 是 {(幣別, 幣別): 折減率}，兩個方向都查。找不到就報錯，不猜。"""
    if (a, b) in haircuts:
        return haircuts[(a, b)]
    if (b, a) in haircuts:
        return haircuts[(b, a)]
    raise KeyError(f"沒有 {a}/{b} 的折減率")


def currency_margin(balances_base, haircuts):
    """回傳 {"margin": 總保證金, "steps": [...], "uncovered": [...]}。

    balances_base：{幣別: 基準貨幣等值的淨清算值}，可正可負。
    haircuts：{(幣別, 幣別): 折減率}。
    steps：每段 (負餘額幣別, 拿來抵銷的正餘額幣別, 抵銷金額, 折減率, 這段保證金)。
    uncovered：[(幣別, 還沒被抵銷的金額)]，代表沒有足夠的正餘額，這個程式不替它編折減率。
    """
    negatives = sorted(
        ((c, -v) for c, v in balances_base.items() if v < -EPS),
        key=lambda x: -x[1],
    )  # 最大的負餘額先處理（我的解讀）
    positives = {c: v for c, v in balances_base.items() if v > EPS}

    steps = []
    uncovered = []
    total = 0.0
    for cur, need in negatives:
        for pos in sorted(positives, key=lambda p: _haircut(haircuts, cur, p)):
            if need <= EPS:
                break
            avail = positives[pos]
            if avail <= EPS:
                continue
            used = min(need, avail)
            rate = _haircut(haircuts, cur, pos)
            margin = used * rate
            steps.append((cur, pos, used, rate, margin))
            total += margin
            positives[pos] = avail - used
            need -= used
        if need > EPS:
            uncovered.append((cur, need))
    return {"margin": total, "steps": steps, "uncovered": uncovered}


def implied_haircut(margin_change, amount):
    """下單預覽的保證金變動 ÷ 成交金額 = 這一筆隱含的比例。amount 必須 > 0。"""
    if amount <= 0:
        raise ValueError("amount 必須 > 0")
    return margin_change / amount


def rounding_band(margin_change, amount, step=1.0):
    """預覽畫面把保證金顯示到 step（例如整數美元）時，真實比例可能落在的範圍 (下限, 上限)。

    只考慮保證金顯示值的四捨五入；amount 本身也是預覽的估算值，這裡不處理。
    """
    half = step / 2.0
    return ((margin_change - half) / amount, (margin_change + half) / amount)


def preview_consistent(margin_change, amount, haircut, step=1.0):
    """預覽的保證金變動，和「amount × haircut」在四捨五入範圍內對得上嗎？

    只能說「對得上／對不上」；對得上不證明 IBKR 的比例本身正確，只證明這一筆量測與我假設的比例一致。
    """
    lo, hi = rounding_band(margin_change, amount, step)
    return lo - EPS <= haircut <= hi + EPS
