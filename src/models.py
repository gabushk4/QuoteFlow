from decimal import Decimal

class Product:
    """A product in the catalogue."""
    def __init__(self, code: str, name: str, price: str) -> None:
        self.code = code
        self.name = name
        self.price = Decimal(price)
        
class SubmissionLine: 
    """A line in a submission"""
    def __init__(self, product: Product, quantity: str) -> None:
        self.product = product
        self.quantity = Decimal(quantity)
        self.__subtotal = product.price * Decimal(quantity)
    
    def get_subtotal(self) -> Decimal:
        return self.__subtotal.quantize(Decimal("0.01"))
        
class Submission: 
    """A submission following a demand"""
    def __init__(self, lines: list[SubmissionLine], taxes: dict[str, Decimal]) -> None:     
        self.lines = lines   
        self.__subtotal =  sum(
            (line.get_subtotal() for line in lines), 
            Decimal("0.00")
        )
        
        # ["TVQ": 40.12$, ...]
        self.__taxes_totals = {
            key: (self.__subtotal * tax).quantize(Decimal("0.01"))
            for key , tax in taxes.items()
        }
        
        self.__total = self.__subtotal + sum(self.__taxes_totals.values())
    
    def get_subtotal(self) -> Decimal:
        return self.__subtotal.quantize(Decimal("0.01"))
    
    def get_total(self) -> Decimal:
        return self.__total.quantize(Decimal("0.01"))
    
    def get_taxes_totals(self) -> dict[str, Decimal]:
        return {
            key: value.quantize(Decimal("0.01")) 
            for key, value in self.__taxes_totals.items()
        }
        
        