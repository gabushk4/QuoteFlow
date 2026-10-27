from decimal import Decimal
import os
from pathlib import Path

from src.constants.env_keys import keys
from src.constants.file import PROJECT_ROOT
from src.models import Product, Submission, SubmissionLine
from src.utils.csv_reader import read_catalogue, read_demand
from src.utils.pdf_writer import generate_pdf
from src.utils.mail_sender import send_pdf
from src.utils.load_env import load_env

if __package__:
    from .utils.csv_reader import read_catalogue, read_demand
else:
    from utils.csv_reader import read_catalogue, read_demand

PDF_PATH = PROJECT_ROOT / "data" / "submission.pdf"


def build_submission(
    catalogue: dict[str, dict[str, str]],
    demand: dict[str, dict[str, str]],
    taxes: dict[str, Decimal],
    client: dict[str, str],
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

    return Submission(lines, taxes, client)


def main() -> None:
	catalogue = read_catalogue()
	demand = read_demand()

	taxes = {
        "TPS": Decimal("0.05"),
	    "TVQ": Decimal("0.09975"),
	}

	
	# client info input
	client = dict()
	client_infos_ok = False
	while(not client_infos_ok):
		print("==== Infos du client ====")
		client["name"] = input("Nom, Prenom: ")	
		client["email"] = input("Courriel: ")

  
		client_infos_ok = input(f"""
Les informations du client sont exactes ? (O/N) 

Nom, Prenom: {client['name']}
Courriel: {client['email']}

"O" pour OK, "N" | "Enter" pour corriger """).upper() == "O"
	# end client infos input
 
	#build submission with demand and client info
	submission = build_submission(catalogue, demand, taxes, client)
 
	print("""
==== Résumé de la soumission ====
""")
	name_width = max(
		[len("Produit")] + [len(line.product.name) for line in submission.lines]
	)
	
	quantity_width = 8
	subtotal_width = 12
	separator = " | "

	print(f"{'Produit':<{name_width}}{separator}{'Quantité':>{quantity_width}}{separator}'Sous-total':>{subtotal_width}")
	print("-" * (name_width + quantity_width + subtotal_width + (len(separator) * 2)))

	for line in submission.lines:
		print(
			f"{line.product.name:<{name_width}}{separator}"
			f"{line.quantity:>{quantity_width}}{separator}"
			f"{line.get_subtotal():>{subtotal_width - 2}.2f} $"
		)
    
	input("""
Appuyez sur Entrée pour générer le PDF """)
    
	generate_pdf(submission, PDF_PATH)
	print(f"""PDF généré avec succès !
Voir dans {PDF_PATH}
""")
	
	env = load_env()
	input(f"Appuyez sur Entrée pour envoyer le PDF à l'adresse: {client['email']}")
	send_pdf(PDF_PATH, to=client['email'])
	print(f"""
PDF envoyé avec succès à l'adresse: {client['email']}
Allez vérifier la boite d'envoi de l'adresse: {env[keys.SMTP_USERNAME]}
""")


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\nOpération annulée.")
	
	
