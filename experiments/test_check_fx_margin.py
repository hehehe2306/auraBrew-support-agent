"""check_fx_margin.py 的測試：只用 IBKR 官方範例的示範數字與假數字，不含任何真實帳戶資料。
用法：python -m unittest experiments.test_check_fx_margin -v
"""
import unittest

from experiments import check_fx_margin as fx


class OfficialExample(unittest.TestCase):
    """IBKR「Currency margin calculation」範例：基準貨幣 USD。"""

    def setUp(self):
        self.balances = {
            "EUR": fx.to_base(-14362.69, 0.72860),   # 約 -19712.72
            "KRW": fx.to_base(6692613.37, 1330.0),   # 約 5032.04
            "USD": 15073.07,
        }
        self.haircuts = {("USD", "EUR"): 0.025, ("USD", "KRW"): 0.10, ("EUR", "KRW"): 0.10}

    def test_base_conversion_matches_official_numbers(self):
        self.assertAlmostEqual(self.balances["EUR"], -19712.723, places=2)
        self.assertAlmostEqual(self.balances["KRW"], 5032.04, places=2)

    def test_total_margin_matches_official_840_79(self):
        r = fx.currency_margin(self.balances, self.haircuts)
        self.assertAlmostEqual(r["margin"], 840.79, delta=0.01)

    def test_steps_match_official_margin1_and_margin2(self):
        r = fx.currency_margin(self.balances, self.haircuts)
        self.assertEqual(len(r["steps"]), 2)
        # 先用折減率最低的 USD 抵銷，再用 KRW
        self.assertEqual(r["steps"][0][:2], ("EUR", "USD"))
        self.assertAlmostEqual(r["steps"][0][4], 376.82, delta=0.01)
        self.assertEqual(r["steps"][1][:2], ("EUR", "KRW"))
        self.assertAlmostEqual(r["steps"][1][4], 463.97, delta=0.01)
        self.assertEqual(r["uncovered"], [])


class OtherCases(unittest.TestCase):
    def test_no_negative_balance_needs_no_margin(self):
        r = fx.currency_margin({"USD": 1000.0, "EUR": 500.0}, {("USD", "EUR"): 0.025})
        self.assertEqual(r["margin"], 0.0)
        self.assertEqual(r["steps"], [])

    def test_cheapest_haircut_used_first_and_only_as_needed(self):
        # 負 100，USD 有 300（折減率 0.02）、KRW 有 300（0.10）：只會用到 USD
        r = fx.currency_margin(
            {"EUR": -100.0, "USD": 300.0, "KRW": 300.0},
            {("EUR", "USD"): 0.02, ("EUR", "KRW"): 0.10},
        )
        self.assertAlmostEqual(r["margin"], 2.0)
        self.assertEqual(len(r["steps"]), 1)

    def test_haircut_lookup_works_in_both_directions(self):
        r = fx.currency_margin({"EUR": -100.0, "USD": 100.0}, {("USD", "EUR"): 0.025})
        self.assertAlmostEqual(r["margin"], 2.5)

    def test_missing_haircut_raises_instead_of_guessing(self):
        with self.assertRaises(KeyError):
            fx.currency_margin({"EUR": -100.0, "USD": 100.0}, {})

    def test_insufficient_positive_balance_is_reported_not_invented(self):
        r = fx.currency_margin({"EUR": -100.0, "USD": 40.0}, {("EUR", "USD"): 0.025})
        self.assertAlmostEqual(r["margin"], 1.0)
        self.assertEqual(len(r["uncovered"]), 1)
        self.assertEqual(r["uncovered"][0][0], "EUR")
        self.assertAlmostEqual(r["uncovered"][0][1], 60.0)

    def test_two_negatives_largest_first_and_positive_not_double_used(self):
        # 這個測試只是鎖住「我自己的規則」（最大負餘額先抵銷），不是 IBKR 的規則。
        # 手算：A=-100 先用 USD(0.02) 100 -> 2.0，USD 剩 20；
        #       B=-50 用 USD(0.03) 20 -> 0.6，再用 C(0.04) 30 -> 1.2；合計 3.8
        balances = {"A": -100.0, "B": -50.0, "USD": 120.0, "C": 30.0}
        haircuts = {("A", "USD"): 0.02, ("A", "C"): 0.05, ("B", "USD"): 0.03, ("B", "C"): 0.04}
        r = fx.currency_margin(balances, haircuts)
        self.assertAlmostEqual(r["margin"], 3.8)
        self.assertEqual(r["uncovered"], [])

    def test_to_base_rejects_non_positive_rate(self):
        with self.assertRaises(ValueError):
            fx.to_base(100.0, 0)


class PreviewMeasurement(unittest.TestCase):
    """下單預覽的量測怎麼拿來對照（全部假數字）。"""

    def test_short_foreign_position_margin_is_amount_times_haircut(self):
        # 假設：賣出 50,000 USD 等值的外幣 -> 外幣負餘額 -50,000，美元正餘額足夠，折減率 3%
        r = fx.currency_margin({"EUR": -50000.0, "USD": 900000.0}, {("USD", "EUR"): 0.03})
        self.assertAlmostEqual(r["margin"], 1500.0)

    def test_buying_foreign_currency_adds_no_currency_margin(self):
        # 買進 -> 外幣是正餘額，沒有負餘額要抵銷，保證金 0（對應預覽的「買進 Change = 0」）
        r = fx.currency_margin({"EUR": 50000.0, "USD": 900000.0}, {("USD", "EUR"): 0.03})
        self.assertEqual(r["margin"], 0.0)

    def test_implied_haircut(self):
        self.assertAlmostEqual(fx.implied_haircut(1500.0, 50000.0), 0.03)

    def test_implied_haircut_rejects_non_positive_amount(self):
        with self.assertRaises(ValueError):
            fx.implied_haircut(100.0, 0)

    def test_preview_consistent_when_rounded_display_matches(self):
        # 顯示 1500，實際可能是 1499.5～1500.5：0.03 在範圍內
        self.assertTrue(fx.preview_consistent(1500.0, 50000.0, 0.03))

    def test_preview_consistent_allows_rounding_gap(self):
        # 真實 3% 但顯示 1500.4 四捨五入成 1500，仍算對得上
        self.assertTrue(fx.preview_consistent(1500.0, 50000.0, 1500.4 / 50000.0))

    def test_preview_inconsistent_when_rate_is_clearly_different(self):
        # 若真實比例是 3.1%，預覽應該顯示約 1550，而不是 1500
        self.assertFalse(fx.preview_consistent(1500.0, 50000.0, 0.031))

    def test_rounding_band_is_symmetric_around_displayed_value(self):
        lo, hi = fx.rounding_band(1500.0, 50000.0)
        self.assertAlmostEqual(lo, 1499.5 / 50000.0)
        self.assertAlmostEqual(hi, 1500.5 / 50000.0)


class InitialVsMaintenance(unittest.TestCase):
    """初始與維持保證金可能是不同的比例（預覽量到 GBP.USD 是這樣）；全部假數字。"""

    def test_initial_and_maintenance_checked_separately(self):
        amount = 50000.0
        self.assertTrue(fx.preview_consistent(1875.0, amount, 0.0375))  # 初始 3.75%
        self.assertTrue(fx.preview_consistent(1500.0, amount, 0.03))    # 維持 3.0%
        # 把兩個比例對調，就應該對不上
        self.assertFalse(fx.preview_consistent(1875.0, amount, 0.03))
        self.assertFalse(fx.preview_consistent(1500.0, amount, 0.0375))

    def test_doubling_amount_doubles_margin_in_the_model(self):
        # 模型是線性的：數量加倍，保證金加倍（預覽量到 EUR.USD 約 2.00 倍，是對照的目標，不是證明）
        h = {("USD", "EUR"): 0.03}
        a = fx.currency_margin({"EUR": -50000.0, "USD": 900000.0}, h)["margin"]
        b = fx.currency_margin({"EUR": -100000.0, "USD": 900000.0}, h)["margin"]
        self.assertAlmostEqual(b / a, 2.0)


if __name__ == "__main__":
    unittest.main()
