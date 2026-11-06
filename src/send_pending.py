import json
from pathlib import Path

from src.utils.mail_sender import send_pdf
from src.utils.pending_sends import PENDING_SENDS_FILE
from src.utils.gmail_check import save_processed_ids


def send_pending_pdfs() -> None:
    """Send queued PDFs, retaining failed entries for a later retry."""
    if not PENDING_SENDS_FILE.exists():
        print("Aucun PDF en attente d'envoi.")
        return

    pending_lines = PENDING_SENDS_FILE.read_text(encoding="utf-8").splitlines()
    remaining_lines = []
    sent_count = 0

    for line in pending_lines:
        try:
            entry = json.loads(line)
            pdf_path = Path(entry["path"])
            recipient = entry["recipient"]
            if not isinstance(recipient, str):
                raise ValueError("destinataire invalide")

            send_pdf(pdf_path, to=recipient)
            save_processed_ids([entry])
            print(f"PDF envoyé à {recipient}: {pdf_path}")
            sent_count += 1
        except Exception as error:
            print(f"Échec d'envoi de l'entrée en attente: {error}")
            remaining_lines.append(line)

    if remaining_lines:
        PENDING_SENDS_FILE.write_text(
            "\n".join(remaining_lines) + "\n",
            encoding="utf-8",
        )
    else:
        PENDING_SENDS_FILE.unlink()

    print(
        f"Envois terminés: {sent_count}; "
        f"entrées conservées pour réessai: {len(remaining_lines)}."
    )


if __name__ == "__main__":
    send_pending_pdfs()
