import unittest

from scraper import ScraperError, extract_rows, validate_ai_result

# Synthetic HTML fixture for parser unit tests — NOT a real scraper output.
HTML = """
<table>
  <tr><th>Casino</th><th>Bonus</th><th>Wagering</th><th>Min Deposit</th></tr>
  <tr><td>PlayaBets Claim →</td><td>100% up to R3,000</td><td>6x</td><td>R10</td></tr>
  <tr><td>Springbok</td><td>R250 free + R11,500 package</td><td>30x</td><td>R25</td></tr>
  <tr><td>20Bet</td><td>R2,400 + 120 spins</td><td>40x</td><td>R400</td></tr>
</table>
"""


class ScraperTests(unittest.TestCase):
    def test_extract_rows(self):
        rows = extract_rows(HTML)
        self.assertEqual([r["name"] for r in rows], ["PlayaBets", "Springbok", "20Bet"])
        self.assertEqual(rows[0]["bonus_text"], "100% up to R3,000")

    def test_ai_result_validation(self):
        row = extract_rows(HTML)[1]
        result = validate_ai_result(
            {
                "welcome_bonus": row["bonus_text"],
                "wagering_multiplier": 30,
                "minimum_deposit": row["deposit_text"],
            }, row
        )
        self.assertEqual(result["wagering_multiplier"], 30)

    def test_reject_hallucinated_wagering(self):
        row = extract_rows(HTML)[1]
        with self.assertRaises(ScraperError):
            validate_ai_result({
                "welcome_bonus": row["bonus_text"],
                "wagering_multiplier": 35,
                "minimum_deposit": row["deposit_text"],
            }, row)

    def test_reject_ambiguous_wagering(self):
        row = extract_rows(HTML)[1]
        row["wagering_text"] = "3x sports / 30x casino"
        with self.assertRaises(ScraperError):
            validate_ai_result({
                "welcome_bonus": row["bonus_text"],
                "wagering_multiplier": 30,
                "minimum_deposit": row["deposit_text"],
            }, row)


if __name__ == "__main__":
    unittest.main()
