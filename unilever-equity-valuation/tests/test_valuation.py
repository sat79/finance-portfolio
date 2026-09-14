"""Test the actual workbook and rejection of corrupted valuation inputs/outputs."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import verify_model as model


class ValuationTests(unittest.TestCase):
    def setUp(self):
        self.path=model.ROOT/'models/Unilever-Valuation-Reviewed.xlsx'
        self.book=model.read_xlsx(self.path)
    def test_distributed_model_reconciles(self):
        result=model.verify(self.path)
        self.assertEqual(result['comparisons'],98)
        self.assertAlmostEqual(result['dcf_eur_per_share'],63.87,places=2)
    def test_corrupted_valuation_rejected(self):
        self.book['DCF']['B41']['value']+=1
        with patch.object(model,'read_xlsx',return_value=self.book):
            with self.assertRaisesRegex(ValueError,'Mismatch'):model.verify(self.path)
    def test_zero_shares_rejected(self):
        self.book['DCF']['B14']['value']=0
        with patch.object(model,'read_xlsx',return_value=self.book):
            with self.assertRaisesRegex(ValueError,'share count'):model.verify(self.path)
    def test_invalid_method_weights_rejected(self):
        self.book['Summary']['B8']['value']=-1
        with patch.object(model,'read_xlsx',return_value=self.book):
            with self.assertRaisesRegex(ValueError,'method weights'):model.verify(self.path)


if __name__=='__main__':unittest.main()
