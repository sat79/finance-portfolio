import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import analyse as m


class CreditTests(unittest.TestCase):
    def test_zero_interest(self):
        self.assertEqual(m.payment(1200,0,12),100)
    def test_amortises(self):
        balance=10000
        p=m.payment(balance,.12,36)
        for _ in range(36):balance=balance*1.01-p
        self.assertAlmostEqual(balance,0,places=7)
    def test_loss_identity_and_bounds(self):
        self.assertEqual(m.expected_loss(.1,.5,10000),500)
        for values in [(1.1,.5,100),(.2,-1,100),(.1,.5,-1),(float('nan'),.5,100)]:
            with self.assertRaises(ValueError):m.expected_loss(*values)
    def test_invalid_loan(self):
        for values in [(0,.1,12),(100,-.1,12),(100,.1,0),(100,.1,1.5)]:
            with self.assertRaises(ValueError):m.payment(*values)
    def test_auc_ties_and_order(self):
        self.assertEqual(m.auc([0,1],[.2,.2]),.5)
        self.assertEqual(m.auc([0,1],[.1,.9]),1)
        self.assertEqual(m.auc([0,1],[.9,.1]),0)
        self.assertIsNone(m.auc([1,1],[.1,.9]))
    def test_outcome_not_in_grade(self):
        row={'utilisation':.7,'prior_arrears':0,'default_12m':0}
        g=m.grade(row);row['default_12m']=1
        self.assertEqual(m.grade(row),g)
    def test_pd_uses_training_only(self):
        rows=m.load_data(m.ROOT/'data/synthetic_applications.csv')
        train=[x for x in rows if x['vintage_year']==2022]
        original=m.fit_pd(train)
        for row in rows:
            if row['vintage_year']!=2022:row['default_12m']=1-row['default_12m']
        self.assertEqual(original,m.fit_pd(train))
    def test_stress_same_book_higher_loss(self):
        rows=m.load_data(m.ROOT/'data/synthetic_applications.csv');pds=m.fit_pd(rows[:600])
        base=m.evaluate(rows[1200:],pds,.1);stress=m.evaluate(rows[1200:],pds,.1,True)
        self.assertEqual(base['approved'],stress['approved'])
        self.assertGreater(stress['expected_loss_gbp'],base['expected_loss_gbp'])
        self.assertLess(stress['expected_contribution_gbp'],base['expected_contribution_gbp'])
    def test_duplicate_rejected(self):
        with (m.ROOT/'data/synthetic_applications.csv').open() as f:lines=f.readlines()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.csv';p.write_text(''.join(lines+[lines[1]]))
            with self.assertRaisesRegex(ValueError,'Duplicate'):m.load_data(p)
    def test_zero_cutoff_declines_all(self):
        rows=m.load_data(m.ROOT/'data/synthetic_applications.csv')
        self.assertEqual(m.evaluate(rows,m.fit_pd(rows[:600]),0)['approved'],0)


if __name__=='__main__':unittest.main()
