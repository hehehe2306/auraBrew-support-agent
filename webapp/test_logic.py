"""webapp/logic.py 的測試：全部假數字，不需要 Streamlit。
用法（repo 根目錄）：python -m unittest webapp.test_logic -v
"""
import unittest
from datetime import datetime

from webapp import logic


class Examples(unittest.TestCase):
    def test_consistent_example_passes(self):
        r = logic.run(logic.EXAMPLES["全部對得上"])
        self.assertEqual(r["problems"], [])
        self.assertAlmostEqual(r["leverage"], 1.5)
        self.assertAlmostEqual(r["cushion"], 0.625)
        self.assertAlmostEqual(r["drop_to_zero"], 62500 / 112500)

    def test_mismatch_example_flags_only_excess_liquidity(self):
        r = logic.run(logic.EXAMPLES["超額流動性對不上"])
        self.assertEqual(len(r["problems"]), 1)
        self.assertTrue(r["problems"][0].startswith("[超額流動性]"))

    def test_near_break_example(self):
        # 手算：EL=ELV−MM=15000、AF=ELV−IM=10000、BP=AF×4=40000，欄位一致；
        # 槓桿 300000/100000=3；破線距離 15000/(300000−85000)
        r = logic.run(logic.EXAMPLES["離破線很近"])
        self.assertEqual(r["problems"], [])
        self.assertAlmostEqual(r["leverage"], 3.0)
        self.assertAlmostEqual(r["drop_to_zero"], 15000 / 215000)


class ParseInputs(unittest.TestCase):
    def test_strings_with_commas_are_parsed(self):
        raw = {n: f"{v:,}" for n, v in logic.EXAMPLES["全部對得上"].items()}
        values, errors = logic.parse_inputs(raw)
        self.assertEqual(errors, [])
        self.assertEqual(values["buying_power"], 220000.0)

    def test_blank_and_non_numeric_are_errors_not_filled(self):
        raw = dict(logic.EXAMPLES["全部對得上"])
        raw["initial_margin"] = ""
        raw["buying_power"] = "很多"
        values, errors = logic.parse_inputs(raw)
        self.assertEqual(len(errors), 2)
        self.assertNotIn("initial_margin", values)
        self.assertNotIn("buying_power", values)

    def test_negative_excess_liquidity_is_allowed_and_warned(self):
        raw = dict(logic.EXAMPLES["全部對得上"], excess_liquidity=-100, equity_with_loan_value=37400,
                   available_funds=37400 - 45000, buying_power=(37400 - 45000) * 4)
        values, errors = logic.parse_inputs(raw)
        self.assertEqual(errors, [])
        r = logic.run(values)
        self.assertTrue(r["warnings"])


class Display(unittest.TestCase):
    def test_summary_has_no_judgement_or_advice_words(self):
        for ex in logic.EXAMPLES.values():
            text = "\n".join(logic.summary_lines(logic.run(ex)))
            for w in ("安全", "危險", "建議", "應該", "該買", "該賣"):
                self.assertNotIn(w, text)


class Sheet(unittest.TestCase):
    def test_row_matches_header_and_values(self):
        ex = logic.EXAMPLES["超額流動性對不上"]
        row = logic.sheet_row(ex, logic.run(ex), " 小明 ", now=datetime(2026, 11, 23, 9, 30))
        self.assertEqual(len(row), len(logic.SHEET_HEADER))
        self.assertEqual(row[0], "2026-11-23 09:30:00")
        self.assertEqual(row[1], "小明")
        self.assertEqual(row[2 + len(logic.FIELDS)], "不通過")
        self.assertEqual(row[3 + len(logic.FIELDS)], "超額流動性")

    def test_email_like_nickname_is_dropped(self):
        self.assertEqual(logic.clean_nickname("someone@example.com"), "")

    def test_long_nickname_is_truncated(self):
        self.assertEqual(len(logic.clean_nickname("a" * 50)), logic.NICKNAME_MAX)


class Payload(unittest.TestCase):
    def test_payload_has_token_header_and_row_of_same_length(self):
        ex = logic.EXAMPLES["全部對得上"]
        p = logic.sheet_payload(ex, logic.run(ex), "", "secret", now=datetime(2026, 11, 23))
        self.assertEqual(p["token"], "secret")
        self.assertEqual(len(p["header"]), len(p["row"]))
        import json
        json.dumps(p, ensure_ascii=False)  # 要能轉成 JSON 送出


if __name__ == "__main__":
    unittest.main()
