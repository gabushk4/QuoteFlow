from decimal import Decimal
import unittest
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