from src.constants.file import PROJECT_ROOT
from src.models import Product, Submission, SubmissionLine
from decimal import Decimal
from src.utils.pdf_writer import generate_pdf
from pathlib import Path

if __package__:
	from .utils.csv_reader import read_catalogue, read_demand
else:
	from utils.csv_reader import read_catalogue, read_demand
 
PDF_PATH = PROJECT_ROOT / "data" / "submission.pdf"
 
def main():
	catalogue = read_catalogue()	

	lines = []
	index = 0
	for code, product in catalogue.items():            
		quantity = index % 3 + 1
		lines.append(SubmissionLine(Product(code=code, name=product["name"], price=product["price"]), str(quantity)))
		index = index + 1

	submission = Submission(lines, {
		"TPS": Decimal("0.05"),
		"TVQ": Decimal("0.09975"),
	})

	submission = Submission(lines, {"TPS": Decimal("0.05"), "TVQ": Decimal("0.09975")})	

	generate_pdf(submission, PDF_PATH)
    
	

if __name__ == "__main__":
	main()
	
	
