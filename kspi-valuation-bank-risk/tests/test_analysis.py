"""Financial identities, data failures, sensitivity and clean CLI behaviour."""
from copy import deepcopy
import csv
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import analyse as model
from verify_workbook import verify


class ValuationTests(unittest.TestCase):
    def setUp(self):
        self.config = model.load_json(ROOT / "data/assumptions.json")

    def test_published_scenarios(self):
        expected = model.load_json(ROOT / "data/reference_outputs.json")
        for name in model.CASE_NAMES:
            self.assertAlmostEqual(model.value_case(self.config, name)["value_usd"], expected[name], 8)

    def test_level_dividend_equals_perpetuity(self):
        c = self.config
        for case in c["cases"].values():
            case["dividend_growth"] = [0] * 5
            case["fx_depreciation"] = [0] * 5
        c["terminal_kzt_dividend_growth"] = c["terminal_fx_depreciation"] = 0
        expected = c["quarterly_dividend_assumption_kzt"] * 4 / c["fx_reference_kzt_per_usd"] / model.cost_of_equity(c)
        self.assertAlmostEqual(model.value_case(c, "Base")["value_usd"], expected, 9)

    def test_constant_growth_equals_gordon_model(self):
        c = self.config
        for case in c["cases"].values():
            case["dividend_growth"] = [0.06] * 5
            case["fx_depreciation"] = [0.03] * 5
        c["terminal_kzt_dividend_growth"], c["terminal_fx_depreciation"] = 0.06, 0.03
        growth = 1.06 / 1.03 - 1
        expected = c["quarterly_dividend_assumption_kzt"] * 4 / c["fx_reference_kzt_per_usd"] * (1 + growth) / (model.cost_of_equity(c) - growth)
        self.assertAlmostEqual(model.value_case(c, "Base")["value_usd"], expected, 9)

    def test_zero_dividend(self):
        self.config["quarterly_dividend_assumption_kzt"] = 0
        result = model.value_case(self.config, "Base")
        self.assertEqual(result["value_usd"], 0)
        self.assertEqual(result["terminal_share"], 0)

    def test_dividend_scales_linearly(self):
        base = model.value_case(self.config, "Base")["value_usd"]
        self.config["quarterly_dividend_assumption_kzt"] *= 2
        self.assertAlmostEqual(model.value_case(self.config, "Base")["value_usd"], 2 * base)

    def test_higher_fx_reduces_value(self):
        base = model.value_case(self.config, "Base")["value_usd"]
        self.config["cases"]["Base"]["fx_depreciation"] = [0.15] * 5
        self.assertLess(model.value_case(self.config, "Base")["value_usd"], base)

    def test_higher_discount_reduces_value(self):
        base = model.value_case(self.config, "Base")["value_usd"]
        self.config["additional_risk_premium"] += 0.01
        self.assertLess(model.value_case(self.config, "Base")["value_usd"], base)

    def test_year_five_growth_changes_forecast_and_value(self):
        before = model.value_case(self.config, "Base")
        self.config["cases"]["Base"]["dividend_growth"][4] += 0.05
        after = model.value_case(self.config, "Base")
        self.assertEqual(before["cashflows"][:4], after["cashflows"][:4])
        self.assertGreater(after["value_usd"], before["value_usd"])

    def test_invalid_scalar_inputs(self):
        for key, value in [("fx_reference_kzt_per_usd", 0), ("beta", None),
                           ("beta", True), ("beta", "1.1"), ("beta", math.nan),
                           ("beta", math.inf), ("tax_assumption", 1.1),
                           ("h1_group_net_income_kzt_bn", 0), ("credit_shock", -0.01),
                           ("terminal_fx_depreciation", -1), ("quarterly_dividend_assumption_kzt", -1)]:
            with self.subTest(key=key, value=value):
                c = deepcopy(self.config); c[key] = value
                with self.assertRaises(model.InputError): model.value_case(c, "Base")

    def test_missing_and_misspelled_keys(self):
        for change in ("missing", "extra"):
            c = deepcopy(self.config)
            if change == "missing": del c["beta"]
            else: c["btea"] = 1
            with self.assertRaises(model.InputError): model.value_case(c, "Base")

    def test_unknown_case(self):
        with self.assertRaises(model.InputError): model.value_case(self.config, "Bsae")

    def test_terminal_growth_must_be_below_discount(self):
        self.config["terminal_kzt_dividend_growth"] = 0.50
        with self.assertRaises(model.InputError): model.value_case(self.config, "Base")

    def test_incomplete_forecast_paths(self):
        for path in ([], [0] * 4, [0] * 6, [0, 0, None, 0, 0]):
            c = deepcopy(self.config); c["cases"]["Base"]["dividend_growth"] = path
            with self.assertRaises(model.InputError): model.value_case(c, "Base")

    def test_invalid_forecast_growth(self):
        for field, rate in (("dividend_growth", -1.01), ("fx_depreciation", -1)):
            c = deepcopy(self.config); c["cases"]["Base"][field][2] = rate
            with self.assertRaises(model.InputError): model.value_case(c, "Base")

    def test_funding_and_credit_units(self):
        result = model.earnings_sensitivity(self.config)
        self.assertAlmostEqual(result["funding_expense_kzt_bn"], 78)
        self.assertAlmostEqual(result["credit_loss_expense_kzt_bn"], 73)
        self.assertAlmostEqual(result["after_tax_stress_kzt_bn"], 113.25)

    def test_zero_shocks(self):
        self.config["funding_shock"] = self.config["credit_shock"] = 0
        self.assertEqual(model.earnings_sensitivity(self.config)["after_tax_stress_kzt_bn"], 0)

    def test_full_loss_stops_future_payouts(self):
        self.config["cases"]["Base"]["dividend_growth"][0] = -1
        self.assertEqual(model.value_case(self.config, "Base")["value_usd"], 0)


class DataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.csv = Path(self.temp.name) / "segments.csv"
        with (ROOT / "data/segments.csv").open(encoding="utf-8", newline="") as source:
            self.rows = list(csv.DictReader(source))
        self.controls = model.load_json(ROOT / "data/group_income_controls.json")

    def run_rows(self):
        with self.csv.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["year", "segment", "revenue_kzt_mn", "net_income_kzt_mn"])
            writer.writeheader(); writer.writerows(self.rows)
        return model.analyse_segments(self.csv, ROOT / "sql/segment_analysis.sql", self.controls)

    def test_reported_segment_changes(self):
        rows = {r["segment"]: r for r in self.run_rows()}
        self.assertAlmostEqual(rows["Payments"]["net_income_growth"], 433001 / 381607 - 1)
        self.assertLess(rows["Marketplace"]["net_income_growth"], 0)
        self.assertGreater(rows["Marketplace"]["revenue_growth"], 1)

    def test_missing_prior_year_is_rejected(self):
        self.rows.pop(0)
        with self.assertRaises(model.InputError): self.run_rows()

    def test_duplicate_is_rejected(self):
        self.rows.append(self.rows[0])
        with self.assertRaises(model.InputError): self.run_rows()

    def test_wrong_year_is_rejected(self):
        self.rows[0]["year"] = "2023"
        with self.assertRaises(model.InputError): self.run_rows()

    def test_source_income_must_reconcile(self):
        self.rows[0]["net_income_kzt_mn"] = "1"
        with self.assertRaises(model.InputError): self.run_rows()

    def test_nonfinite_source_is_rejected(self):
        self.rows[0]["revenue_kzt_mn"] = "nan"
        with self.assertRaises(model.InputError): self.run_rows()

    def test_zero_revenue_is_null_not_infinity(self):
        for row in self.rows:
            if row["segment"] == "Payments": row["revenue_kzt_mn"] = "0"
        result = {r["segment"]: r for r in self.run_rows()}["Payments"]
        self.assertIsNone(result["revenue_growth"])
        self.assertIsNone(result["net_margin"])


class DeliveryTests(unittest.TestCase):
    def test_workbook_saved_values(self):
        self.assertGreater(verify(ROOT / "models/KSPI-Valuation-and-Bank-Risk.xlsx"), 70)

    def test_cli_from_another_directory(self):
        with tempfile.TemporaryDirectory(prefix="review with spaces ") as folder:
            output = Path(folder) / "new folder/results.json"
            run = subprocess.run([sys.executable, str(ROOT / "src/analyse.py"),
                                  "--output", str(output), "--verify-reference"],
                                 cwd=folder, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("Base", json.loads(output.read_text()))

    def test_custom_assumptions_do_not_trigger_reference_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            c = model.load_json(ROOT / "data/assumptions.json")
            c["quarterly_dividend_assumption_kzt"] = 800
            input_path, output = Path(folder) / "custom.json", Path(folder) / "output.json"
            input_path.write_text(json.dumps(c))
            command = [sys.executable, str(ROOT / "src/analyse.py"), "--assumptions", str(input_path), "--output", str(output)]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            run = subprocess.run(command + ["--verify-reference"], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertIn("Reference mismatch", run.stderr)

    def test_validation_survives_optimized_python(self):
        with tempfile.TemporaryDirectory() as folder:
            c = model.load_json(ROOT / "data/assumptions.json"); c["beta"] = -2
            input_path, output = Path(folder) / "bad.json", Path(folder) / "output.json"
            input_path.write_text(json.dumps(c))
            run = subprocess.run([sys.executable, "-O", str(ROOT / "src/analyse.py"), "--assumptions", str(input_path), "--output", str(output)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
