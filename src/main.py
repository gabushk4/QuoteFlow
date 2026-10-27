from src.models import Product, Submission, SubmissionLine
from decimal import Decimal

if __package__:
	from .utils.csv_reader import read_catalogue, read_demand
else:
	from utils.csv_reader import read_catalogue, read_demand
 
def main():
	catalogue = read_catalogue()
	demands = read_demand()

	products_list = list([])
	for demand in demands.values():
		code = demand["code"]        
		product_in_catalogue = catalogue[code]
		product = Product(product_in_catalogue["code"], product_in_catalogue["name"], product_in_catalogue["price"])
		products_list.append(SubmissionLine(product, demand["quantity"]))
   
	submission = Submission(products_list, {"TPS": Decimal("0.05"), "TVQ": Decimal("0.09975")})
	print(["code", "name", "price", "quantity", "total"])
	for product in products_list:
		print([product.product.code, product.product.name, product.product.price, product.quantity, product.get_subtotal()])
	print(f"subtotal: {submission.get_subtotal()} | taxes: {submission.get_taxes_totals()} | total: { submission.get_total() }")
     
	

if __name__ == "__main__":
	main()
	
	
