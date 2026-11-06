from decimal import Decimal
import json
import select
import sys
import time

from src.constants.file import PROJECT_ROOT
from src.models import Product, Submission, SubmissionLine
from src.utils.pdf_writer import generate_pdf
from src.utils.mail_sender import send_pdf
from src.utils.pending_sends import PENDING_SENDS_FILE, queue_pdf

from src.utils.gmail_check import ( 
	get_recent_messages, 
	get_message_details, 
	find_text_body, 
	sort_by_keywords, 
	make_gmail_client, 
	get_email_address, 
	save_processed_ids )
from src.utils.gemini import make_gemini_client, make_request
from src.utils.csv_maker import json_to_csv

from src.utils.csv_reader import read_catalogue, read_demand

DATA_PATH = PROJECT_ROOT / "data"
TMP_PATH = PROJECT_ROOT / "tmp"


def confirm_send_with_timeout(prompt: str, timeout: int = 10) -> bool:
	"""Wait up to ``timeout`` seconds for the user to confirm with Enter."""
	print(prompt, end="", flush=True)
	deadline = time.monotonic() + timeout

	if sys.platform == "win32":
		import msvcrt

		while time.monotonic() < deadline:
			if msvcrt.kbhit():
				key = msvcrt.getwch()
				if key == "\x03":
					raise KeyboardInterrupt
				if key in ("\r", "\n"):
					print()
					return True
			time.sleep(0.05)
	else:
		remaining = max(0, deadline - time.monotonic())
		ready, _, _ = select.select([sys.stdin], [], [], remaining)
		if ready:
			sys.stdin.readline()
			return True

	print("\nDélai dépassé; le PDF sera mis en attente.")
	return False


def show_pending_send_command() -> None:
	if PENDING_SENDS_FILE.exists() and PENDING_SENDS_FILE.stat().st_size > 0:
		print("\nPour envoyer les PDF en attente, relancez cette commande depuis la racine du projet:")
		print("python -m src.send_pending")

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

def get_emails(client, catalogue):
	emails = []
	messages = get_recent_messages(client, days=10)
		
	keywords = [keyword for product in catalogue.values() for keyword in [product["name"]]]
	for message in messages:
		message_details = get_message_details(client, message["id"])
		body = find_text_body(message_details["payload"])
		score, _ = sort_by_keywords(body, keywords)
		if score > 0:
			print(f"Email pertinent trouvé: {message['id']} avec score: {score}, body: {body[:50]}...")
			
			emails.append({
				"id": message['id'], 
				"body": body,
				"score": score,
				"sender": get_email_address(message_details)
			})
	print(f"Nombre d'emails pertinents trouvés pour la génération de devis: {len(emails)}")
	return emails

def clean_gemini_output(output: str) -> str:
	"""Remove Markdown fences and surrounding text from Gemini's JSON response."""
	cleaned = output.strip()
	if not cleaned:
		return ""

	lines = cleaned.splitlines()
	if lines[0].strip().startswith("```"):
		lines = lines[1:]
	if lines and lines[-1].strip() == "```":
		lines = lines[:-1]
	cleaned = "\n".join(lines).strip()

	# Gemini may add an explanation before or after the JSON object.
	start = cleaned.find("{")
	end = cleaned.rfind("}")
	if start != -1 and end >= start:
		return cleaned[start:end + 1]
	return cleaned

def verify_gemini_output(json_output: str, catalogue: dict[str, dict[str, str]]) -> {bool, str}:
	"""Verifies if the output from Gemini is a valid JSON according to the expected schema."""
	try:
		data = json.loads(json_output)
		if not isinstance(data, dict):
			return False , "data not a dict"
		if "pertinent" not in data or "lignes" not in data:
			return False , "pertinent or lignes not present"
		if isinstance(data["pertinent"], str):
			value = data["pertinent"].strip().lower()
			if value not in ("true", "false"):
				return False , "pertinent value not true nor false"
			data["pertinent"] = value == "true"
		if not isinstance(data["pertinent"], bool):
			return False , "pertinent value not a boolean"
		if data["pertinent"] is False:
			return False , "data not pertinant"
		if not isinstance(data["lignes"], list):
			return False , "lines are not a list"
		if len(data["lignes"]) == 0:
			return False , "lines count is 0"
		for line in data["lignes"]:
			if not isinstance(line, dict):
				return False , "line not present"
			if "code" not in line or "quantite" not in line:
				return False , "code or quantity not present"
			if not isinstance(line["code"], str) or type(line["quantite"]) is not int:
				return False , "code or quantite types not valid"
			if line["quantite"] <= 0:
				return False , "quantite invalid"
			if line["code"] not in catalogue:
				return False , "code not in catalogue"
		return True , "valid"
	except json.JSONDecodeError as e :
		return False , e

def delete_tmp_files():
	for f in TMP_PATH.glob("*.csv"):
		if f.is_file():
			f.unlink()

def handle_error(email, error_message, errored_items):
	"""Handles errors by logging and storing the errored email."""
	print(error_message)
	delete_tmp_files()
	errored_items.append(email)

	print("Continuons avec l'item suivant...")


def main() -> None:
	pdf_queued_count = 0
	successful_emails = []
	errored_emails = []
	catalogue = read_catalogue()
	emails = [] 
	client = make_gmail_client()

	taxes = {
			"TPS": Decimal("0.05"),
			"TVQ": Decimal("0.09975"),
		}

	# get emails
	try:
		emails = get_emails(client, catalogue)
	except Exception as e:
		print(f"Erreur lors de la récupération des emails: {e}")
		emails = []  # Reset to empty if there's an error

	if(len(emails) == 0):
		print("Aucun email pertinent trouvé pour la génération de devis.")
		show_pending_send_command()
		return

	input(f"Vous avez {len(emails)} nouveaux emails à traiter. Appuyez sur Entrée pour les traiter...")
	print("Traitement des emails pour la génération de devis...")
	gemini_client = make_gemini_client()

	for email in emails:
		print(f"Traitement de l'email de l'expéditeur: {email['sender']} avec score: {email['score']}")		
		print("Génération de la demande de devis à partir du contenu de l'email...")

		demand_json = clean_gemini_output(
			make_request(gemini_client, email['body'], str(catalogue))
		)
		verified , reason = verify_gemini_output(demand_json, catalogue)
		if not verified:
			handle_error(email, 
			             f"Erreur: La sortie de Gemini n'est pas valide en raison de {reason} pour l'email de l'expéditeur: {email['sender']}. Sortie: {demand_json}", 
						 errored_emails)
			if(reason == "data not pertinant"):
				save_processed_ids([email["id"]])
			continue

		# setting client info
		client = {
			"name": email['sender'].split('@')[0],  # Use the part before '@' as a default name
			"email": email['sender'],
		}

		# decode json to valid submission object
		try:
			json_data = json.loads(demand_json)
			demand_rows = [
				{"code": line["code"], "quantity": line["quantite"]}
				for line in json_data["lignes"]
			]
			demand_path = json_to_csv(
				demand_rows,
				csv_file_path=TMP_PATH / f"csv_{email["id"]}.csv",
				fieldnames=["code", "quantity"]
			)
			demand = read_demand(demand_path)
			submission = build_submission(catalogue, demand, taxes, client)
		except Exception as e:
			handle_error(email, f"Erreur lors de la génération de la demande de devis pour l'email de l'expéditeur: {email['sender']}. Erreur: {e}", errored_emails)
			continue
		print(f"Demande de devis générée avec succès.")
		print(f"Génération du PDF")
		pdf_path = DATA_PATH / f"submission_{email['sender']}_{email['id']}.pdf"
		try:
			generate_pdf(submission, pdf_path)
		except Exception as e:
			handle_error(email, f"Erreur lors de la génération du PDF pour l'email de l'expéditeur: {email['sender']}. Erreur: {e}", errored_emails)
			continue

		confirmed = confirm_send_with_timeout(
			f"Appuyez sur Entrée dans les 10 secondes pour envoyer le PDF à {client['email']}... "
		)
		if not confirmed:
			try:
				pdf_queued_count += 1
				queue_pdf(pdf_path, client["email"], email["id"])
				save_processed_ids([email])
			except Exception as e:
				handle_error(email, f"Erreur lors de la mise en attente du PDF {pdf_path}: {e}", errored_emails)
			continue

		try:
			send_pdf(pdf_path, to=client['email'])
		except Exception as e:
			handle_error(email, f"Erreur lors de l'envoi du PDF à l'email de l'expéditeur: {client['email']}. Erreur: {e}", errored_emails)
			continue
		print(f"PDF envoyé avec succès à l'adresse: {client['email']}")
		successful_emails.append(email)
	try:
		save_processed_ids(successful_emails)
	except Exception as e:
		delete_tmp_files()
		print("Impossible de sauvegarder les identifiants des emails envoyés ou processés")
		print(f"Erreur: {e}")

	if pdf_queued_count > 0:
		show_pending_send_command()

	delete_tmp_files()


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		delete_tmp_files()
		print("\nOpération annulée.")
	
	
