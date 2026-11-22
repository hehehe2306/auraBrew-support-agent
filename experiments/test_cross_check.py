"""cross_check.py 的測試：全部假數字。
用法：python -m unittest experiments.test_cross_check -v
"""
import unittest

from experiments import cross_check as cc


def summary(**over):
    """假帳戶：淨值 100000、持倉 150000、維持保證金 37500、初始 45000，欄位彼此一致。"""
    s = {
        "net_liquidation": 100000.0, "equity_with_loan_value": 100000.0,
        "initial_margin": 45000.0, "maintenance_margin": 37500.0,
        "available_funds": 55000.0, "excess_liquidity": 62500.0, "buying_power": 220000.0,
        "gross_position_value": 150000.0,
    }
    s.update(over)
    return s


def metrics(**over):
    m = {"date": "2026-11-24", "leverage": 1.5, "cushion_primary_pct": 62.5, "el_gap": 0.0}
    m.update(over)
    return m


class Export(unittest.TestCase):
    def test_ratios_match_hand_calculation(self):
        e = cc.export(summary(), "2026-11-24")
        self.assertEqual(e["leverage"], 1.5)
        self.assertEqual(e["cushion_pct"], 62.5)
        self.assertEqual(e["d_star_pct"], round(62500 / 112500 * 100, 4))  # EL / (V − MM)
        self.assertEqual(e["mm_to_position_pct"], 25.0)
        self.assertEqual(e["checks"], {"available_funds": True, "excess_liquidity": True, "buying_power": True})

    def test_export_contains_no_money_amounts(self):
        e = cc.export(summary(), "2026-11-24")
        for key in ("net_liquidation", "excess_liquidity", "gross_position_value", "buying_power"):
            self.assertNotIn(key, e)

    def test_el_mismatch_is_flagged(self):
        e = cc.export(summary(excess_liquidity=63000.0), "2026-11-24")
        self.assertFalse(e["checks"]["excess_liquidity"])

    def test_missing_fields_give_none(self):
        s = summary()
        del s["buying_power"]
        del s["gross_position_value"]
        e = cc.export(s, "2026-11-24")
        self.assertIsNone(e["checks"])
        self.assertIsNone(e["leverage"])


class Compare(unittest.TestCase):
    def setUp(self):
        self.audit = cc.export(summary(), "2026-11-24")
        self.stress = {"d_star_el_pct": round(62500 / 112500 * 100, 2)}

    def results(self, rows):
        return [r[4] for r in rows]

    def test_all_agree(self):
        rows, notes = cc.compare(self.audit, metrics(), self.stress)
        self.assertEqual(self.results(rows), ["一致"] * 4)
        self.assertEqual(notes, [])

    def test_rounding_within_tolerance_is_agreement(self):
        rows, _ = cc.compare(self.audit, metrics(cushion_primary_pct=62.53, leverage=1.51), self.stress)
        self.assertEqual(self.results(rows)[:2], ["一致", "一致"])

    def test_difference_beyond_tolerance_is_flagged_not_explained(self):
        rows, _ = cc.compare(self.audit, metrics(cushion_primary_pct=62.7), self.stress)
        name, a, b, diff, res = rows[1]
        self.assertEqual(res, "不一致")
        self.assertAlmostEqual(diff, -0.2)

    def test_el_consistency_disagreement(self):
        rows, _ = cc.compare(self.audit, metrics(el_gap=500.0), self.stress)
        self.assertEqual(rows[3][4], "不一致")

    def test_missing_skill_values_are_not_obtained(self):
        rows, notes = cc.compare(self.audit, metrics(cushion_primary_pct=None), None)
        self.assertEqual(rows[1][4], "未取得")
        self.assertEqual(rows[2][4], "未取得")
        self.assertTrue(any("stress.json" in n for n in notes))

    def test_date_mismatch_is_noted(self):
        _, notes = cc.compare(self.audit, metrics(date="2026-11-23"), self.stress)
        self.assertTrue(any("日期不同" in n for n in notes))

    def test_render_has_no_judgement_words(self):
        rows, notes = cc.compare(self.audit, metrics(cushion_primary_pct=70.0), self.stress)
        text = cc.render(rows, notes, ["a", "b"])
        for w in ("安全", "危險", "建議你", "應該降"):
            self.assertNotIn(w, text)


if __name__ == "__main__":
    unittest.main()
