"""Synthetic fixture tests for Study 1 schema guards; no human data are used."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("study1_analysis", ROOT / "code" / "study1_analysis.py")
assert SPEC and SPEC.loader
ANALYSIS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALYSIS)


def fixture() -> pd.DataFrame:
    rows = []
    for condition, period in [("DAI", 1), ("SAI", 2)]:
        for target_status, ordinal_code, primary_binary in [(0, 0, 0), (1, 2, 1)]:
            rows.append({
                "data_status": "SYNTHETIC_ONLY_NOT_EMPIRICAL",
                "participant_id": "SYN_P001",
                "session_id": f"SYN_P001_N{period}",
                "condition": condition,
                "period": period,
                "order": 1,
                "stimulus_id": f"S0{period}",
                "unit_id": f"U{target_status}",
                "target_status": target_status,
                "report_eligible": 1,
                "report_status": "ELIGIBLE",
                "ordinal_code": ordinal_code,
                "primary_binary": primary_binary,
                "delivered_word_count": 100,
            })
    return pd.DataFrame(rows)


class Study1SchemaTests(unittest.TestCase):
    def test_valid_fixture_reaches_primary_dataset(self) -> None:
        data = ANALYSIS.validate(fixture())
        primary, flow = ANALYSIS.primary_dataset(data)
        self.assertEqual(len(primary), 4)
        self.assertEqual(int(flow.iloc[-1]["n_unit_rows"]), 4)

    def test_ambiguous_code_is_not_primary_binary(self) -> None:
        data = fixture()
        data.loc[0, "ordinal_code"] = 1
        data.loc[0, "primary_binary"] = np.nan
        valid = ANALYSIS.validate(data)
        primary, _ = ANALYSIS.primary_dataset(valid)
        self.assertEqual(len(primary), 3)

    def test_mismatched_binary_is_rejected(self) -> None:
        data = fixture()
        data.loc[0, "primary_binary"] = 1
        with self.assertRaisesRegex(ValueError, "disagrees"):
            ANALYSIS.validate(data)

    def test_non_synthetic_data_are_refused_by_default(self) -> None:
        data = fixture()
        data.loc[:, "data_status"] = "EMPIRICAL_POST_ETHICS"
        with self.assertRaisesRegex(ValueError, "non-synthetic"):
            ANALYSIS.validate(data)

    def test_no_recall_is_missing_not_absent(self) -> None:
        data = fixture()
        data.loc[0, "report_status"] = "NO_RECALL"
        data.loc[0, "report_eligible"] = 0
        data.loc[0, "ordinal_code"] = np.nan
        data.loc[0, "primary_binary"] = np.nan
        valid = ANALYSIS.validate(data)
        primary, _ = ANALYSIS.primary_dataset(valid)
        self.assertEqual(len(primary), 3)


if __name__ == "__main__":
    unittest.main()
