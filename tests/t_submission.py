from decimal import Decimal
import unittest
from src.main import build_submission
from src.models import Product, Submission, SubmissionLine

class SubmissionTest (unittest.TestCase):
    
    __product = Product("123", "TV", "100")
    __line = SubmissionLine(__product, "2")
    __taxes = {
        "TPS": Decimal("0.05"),
        "TVQ": Decimal("0.09975"),
    }
    
    def test_subtotal(self):
        self.assertEqual(self.__line.get_subtotal(), 200)
    
    def test_taxes(self):
        submission = Submission([self.__line], self.__taxes)
        self.assertEqual(submission.get_taxes_totals(), {"TPS": Decimal("10"), "TVQ": Decimal("19.95")})
    
    def test_total(self):
        submission = Submission([self.__line], self.__taxes)
        self.assertEqual(submission.get_total(), Decimal("229.95"))

    def test_build_submission_from_demand(self):
        catalogue = {
            "P001": {"name": "TV", "price": "100"},
            "P002": {"name": "Ordinateur", "price": "500"},
        }
        demand = {
            "P001": {"quantity": "2"},
            "P002": {"quantity": "1"},
        }

        submission = build_submission(catalogue, demand, self.__taxes)

        self.assertEqual(submission.get_subtotal(), Decimal("700.00"))
        self.assertEqual(submission.get_total(), Decimal("804.82"))