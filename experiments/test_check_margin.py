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
