"""check_margin.py 的測試：全部使用假數字，確認抓得到不一致、不會永遠回 OK。
用法：python -m unittest experiments.test_check_margin -v
"""
import unittest

from experiments import check_margin as cm


def fake(**over):
    """假帳戶：ELV 100000、初始保證金 30000、維持保證金 20000。"""
    s = {
        "net_liquidation": 100000.0,
        "equity_with_loan_value": 100000.0,
        "initial_margin": 30000.0,
        "maintenance_margin": 20000.0,
        "available_funds": 70000.0,
        "excess_liquidity": 80000.0,
        "buying_power": 280000.0,
    }
    s.update(over)
    return s


class CheckMargin(unittest.TestCase):
    def test_consistent_account_passes(self):
        self.assertEqual(cm.check(fake()), [])

    def test_no_positions_passes(self):
        s = fake(initial_margin=0, maintenance_margin=0,
                 available_funds=100000.0, excess_liquidity=100000.0, buying_power=400000.0)
        self.assertEqual(cm.check(s), [])

    def test_wrong_available_funds_is_caught(self):
        problems = cm.check(fake(available_funds=60000.0))
        self.assertTrue(any("可用資金" in p for p in problems))

    def test_wrong_excess_liquidity_is_caught(self):
        problems = cm.check(fake(excess_liquidity=70000.0))
        self.assertTrue(any("超額流動性" in p for p in problems))

    def test_wrong_buying_power_is_caught(self):
        problems = cm.check(fake(buying_power=210000.0))  # 當成 3 倍
        self.assertTrue(any("購買力" in p for p in problems))

    def test_one_cent_rounding_is_tolerated(self):
        self.assertEqual(cm.check(fake(available_funds=70000.01, buying_power=280000.04)), [])

    def test_real_summary_with_one_cent_rounding_passes(self):
        # 假數字，但捨入特性和真實帳戶摘要相同（真實數字不進 repo）：
        # ELV - 初始保證金 = 166612.47 但回報 166612.48（浮點差 0.0100000000093，舊的比較會誤判）；可用資金 x 4 = 666449.92 但回報 666449.91
        s = fake(equity_with_loan_value=199087.02, net_liquidation=199000.0,
                 initial_margin=32474.55, maintenance_margin=40000.0,
                 available_funds=166612.48, excess_liquidity=159087.02,
                 buying_power=666449.91)
        self.assertEqual(cm.check(s), [])

    def test_glossary_variant_tolerates_the_same_rounding(self):
        s = fake(equity_with_loan_value=199087.02, net_liquidation=199000.0,
                 initial_margin=32474.55, maintenance_margin=40000.0,
                 available_funds=166612.48, excess_liquidity=159087.02,
                 buying_power=666449.91)
        self.assertEqual(cm.check(dict(s, prev_day_elv=200087.02)), [])      # 前日 ELV 較高：兩算式相同
        self.assertTrue(any("詞彙表版" in p for p in cm.check(dict(s, prev_day_elv=198087.02))))  # 較低：不同

    def test_two_cent_difference_is_still_caught(self):
        self.assertTrue(any("可用資金" in p for p in cm.check(fake(available_funds=70000.02))))

    def test_missing_field_is_reported(self):
        s = fake()
        del s["buying_power"]
        self.assertEqual(cm.check(s), ["[缺欄位] buying_power"])

    def test_prev_day_elv_variant_only_checked_when_given(self):
        # 前日 ELV 較低時，詞彙表版的購買力較小，與 4x 可用資金不同
        problems = cm.check(fake(prev_day_elv=90000.0))
        self.assertTrue(any("詞彙表版" in p for p in problems))
        self.assertEqual(cm.check(fake(prev_day_elv=100000.0)), [])

    def test_negative_excess_liquidity_warns_but_is_not_an_error(self):
        s = fake(maintenance_margin=110000.0, excess_liquidity=-10000.0)
        self.assertEqual(cm.check(s), [])
        self.assertEqual(len(cm.warnings(s)), 1)
        self.assertEqual(cm.warnings(fake()), [])


if __name__ == "__main__":
    unittest.main()
