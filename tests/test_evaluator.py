import unittest
from brief_gate.evaluator import evaluate_asset

class TestBriefGate(unittest.TestCase):
    def setUp(self):
        self.sample_brief = {
            "brief_title": "Apex Endurance Campaign",
            "brand": "Apex Performance",
            "min_words": 10,
            "max_words": 150,
            "mandatory_keywords": ["electrolyte", "cramping", "Apex"],
            "forbidden_words": ["miracle", "cure", "cheap"],
            "mandatory_disclaimers": ["These statements have not been evaluated by the FDA"]
        }

    def test_passing_asset(self):
        asset = (
            "Apex is the clinically dosed electrolyte supplement engineered to stop mid-race cramping. "
            "Built for marathon runners and endurance athletes who need pure hydration without gut bloat. "
            "These statements have not been evaluated by the FDA."
        )
        res = evaluate_asset(self.sample_brief, asset)
        self.assertEqual(res.verdict, "PASS")
        self.assertGreaterEqual(res.score, 85)

    def test_blocked_asset_with_forbidden_term(self):
        asset = (
            "Apex is a miracle cure for all your cramping problems.\n"
            "These statements have not been evaluated by the FDA."
        )
        res = evaluate_asset(self.sample_brief, asset)
        self.assertEqual(res.verdict, "BLOCK")
        self.assertTrue(any(f.rule_name == "forbidden_term" for f in res.findings))

    def test_personal_attributes_violation(self):
        asset = (
            "Are you suffering from dehydration headaches during marathon training? "
            "Apex electrolyte formula stops cramping. "
            "These statements have not been evaluated by the FDA."
        )
        res = evaluate_asset(self.sample_brief, asset)
        self.assertEqual(res.verdict, "BLOCK")
        self.assertTrue(any("Meta Advertising Standards" in f.message for f in res.findings))

if __name__ == "__main__":
    unittest.main()
