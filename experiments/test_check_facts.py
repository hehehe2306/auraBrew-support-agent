"""check_facts.py 的測試：確認它真的抓得到漂移，而不是永遠回 OK。
用法：python -m unittest experiments.test_check_facts -v
"""
import unittest
from pathlib import Path

from experiments import check_facts as cf

ROOT = Path(__file__).resolve().parent.parent


class CheckFacts(unittest.TestCase):
    def setUp(self):
        self.data = cf.load()
        self.manual = (ROOT / self.data["manual_file"]).read_text(encoding="utf-8")

    def test_current_manual_is_consistent(self):
        self.assertEqual(cf.check(self.data, self.manual), [])

    def test_derived_saving_is_460(self):
        self.assertEqual(cf.compute_derived(self.data, cf.values(self.data))["bundle_saving"], 460)

    def test_price_change_without_manual_update_is_caught(self):
        problems = cf.check(self.data, self.manual, {"x1_price": 5280})
        self.assertTrue(any("x1_price" in p for p in problems))          # 手冊還是 4,980
        self.assertTrue(any("手冊寫 460" in p and "760" in p for p in problems))  # 衍生數字對不上

    def test_edited_manual_with_old_fact_is_caught(self):
        edited = self.manual.replace("3–5 個工作天", "5–7 個工作天")
        problems = cf.check(self.data, edited)
        self.assertTrue(any("ship_days" in p for p in problems))

    def test_stale_derived_number_in_manual_is_caught(self):
        # 事實與價格都改了、手冊價格也改了，但「省 NT$460」沒跟著改
        edited = self.manual.replace("NT$ 4,980", "NT$ 5,280")
        problems = cf.check(self.data, edited, {"x1_price": 5280})
        self.assertEqual(len(problems), 1)
        self.assertIn("760", problems[0])

    def test_affected_lists_derived_and_docs(self):
        lines = cf.affected(self.data, "x1_price")
        self.assertTrue(any("bundle_saving" in l for l in lines))
        self.assertTrue(any("注入案例 7" in l for l in lines))


if __name__ == "__main__":
    unittest.main()
