from decimal import Decimal
from pathlib import Path

from src.constants.file import PROJECT_ROOT
from src.models import Product, Submission, SubmissionLine
from src.utils.csv_reader import read_catalogue, read_demand
from src.utils.pdf_writer import generate_pdf
from src.utils.mail_sender import send_pdf

if __package__:
    from .utils.csv_reader import read_catalogue, read_demand
else:
    from utils.csv_reader import read_catalogue, read_demand

PDF_PATH = PROJECT_ROOT / "data" / "submission.pdf"


def build_submission(
    catalogue: dict[str, dict[str, str]],
    demand: dict[str, dict[str, str]],
    taxes: dict[str, Decimal],
) -> Submission:
    lines: list[SubmissionLine] = []

    for code, demand_row in demand.items():
        product_data = catalogue.get(code)
        if product_data is None:
            raise ValueError(f"Produit inconnu dans le catalogue : {code}")

        quantity = demand_row.get("quantity")
        if quantity is None:
            raise ValueError(f"Quantité absente pour le produit {code}")

        lines.append(
            SubmissionLine(
                Product(
                    code=code,
                    name=product_data["name"],
                    price=product_data["price"],
                ),
                str(quantity),
            )
        )

    return Submission(lines, taxes)


def main() -> None:
    catalogue = read_catalogue()
    demand = read_demand()

    taxes = {
        "TPS": Decimal("0.05"),
        "TVQ": Decimal("0.09975"),
    }

    submission = build_submission(catalogue, demand, taxes)
    generate_pdf(submission, PDF_PATH)
    print("PDF généré avec succès !")
    send_pdf(PDF_PATH, to=None)


if __name__ == "__main__":
    main()
	
	
