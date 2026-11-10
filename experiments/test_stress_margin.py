"""stress_margin.py 的測試：全部使用假數字。
用法：python -m unittest experiments.test_stress_margin -v
"""
import unittest

from experiments import stress_margin as sm


def levered(**over):
    """假帳戶：多頭持倉市值 150000，借了 50000，淨值 100000，維持保證金 25% = 37500。"""
    s = {
        "net_liquidation": 100000.0,
        "equity_with_loan_value": 100000.0,
        "maintenance_margin": 37500.0,
        "excess_liquidity": 62500.0,
        "gross_position_value": 150000.0,
    }
    s.update(over)
    return s


class StressMargin(unittest.TestCase):
    def test_leverage_is_position_over_nlv(self):
        self.assertAlmostEqual(sm.leverage(levered()), 1.5)

    def test_drop_matches_hand_calculation(self):
        # 手算：持倉跌 d 後，現金 -50000 + 150000(1-d)，維持保證金 25% * 150000(1-d)，
        # EL = -50000 + 112500(1-d) = 0  ->  d = 62500/112500
        d, _ = sm.drop_to_zero_excess(levered())
        self.assertAlmostEqual(d, 62500 / 112500)

    def test_excess_is_zero_at_computed_drop(self):
        s = levered()
        d, _ = sm.drop_to_zero_excess(s)
        self.assertAlmostEqual(sm.excess_after_drop(s, d), 0.0, places=6)

    def test_excess_is_zero_matches_full_recompute(self):
        # 不靠公式，直接把持倉價值、現金、保證金重算一次
        s = levered()
        d, _ = sm.drop_to_zero_excess(s)
        v = 150000 * (1 - d)
        elv = -50000 + v
        self.assertAlmostEqual(elv - 0.25 * v, 0.0, places=6)

    def test_no_positions_has_no_drop(self):
        s = levered(gross_position_value=0.0, maintenance_margin=0.0,
                    excess_liquidity=100000.0)
        d, why = sm.drop_to_zero_excess(s)
        self.assertIsNone(d)
        self.assertIn("沒有持倉", why)
        self.assertEqual(sm.leverage(s), 0.0)

    def test_already_negative_excess_is_zero_drop(self):
        d, _ = sm.drop_to_zero_excess(levered(excess_liquidity=-1000.0))
        self.assertEqual(d, 0.0)

    def test_unlevered_account_never_reaches_zero(self):
        # 全額現金買入，跌到 0 超額流動性仍為正
        s = levered(net_liquidation=100000.0, equity_with_loan_value=100000.0,
                    gross_position_value=100000.0, maintenance_margin=25000.0,
                    excess_liquidity=75000.0)
        # 75000 / (100000-25000) = 1.0，剛好 100%，視為不適用
        d, why = sm.drop_to_zero_excess(s)
        self.assertIsNone(d)
        self.assertIn("100%", why)

    def test_cushion(self):
        self.assertAlmostEqual(sm.cushion(levered()), 0.625)
        self.assertIsNone(sm.cushion(levered(equity_with_loan_value=0.0)))

    def test_reported_leverage_mismatch_is_flagged(self):
        r = sm.assess(levered(leverage="3.0"))
        self.assertEqual(len(r["notes"]), 1)
        self.assertEqual(sm.assess(levered(leverage="1.5"))["notes"], [])

    def test_missing_field_is_reported(self):
        s = levered()
        del s["gross_position_value"]
        self.assertIn("gross_position_value", sm.assess(s)["error"])


if __name__ == "__main__":
    unittest.main()
