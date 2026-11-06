import json
from pathlib import Path

from src.constants.file import PROJECT_ROOT


PENDING_SENDS_FILE = PROJECT_ROOT / "data" / "pending_sends.txt"


def queue_pdf(pdf_path: Path, recipient: str, email_id: str) -> None:
    """Append a PDF path and recipient to the deferred-send text file."""
    PENDING_SENDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {"path": str(pdf_path.resolve()), "recipient": recipient, "id": email_id}
    with PENDING_SENDS_FILE.open("a", encoding="utf-8") as pending_file:
        pending_file.write(json.dumps(entry, ensure_ascii=False) + "\n")
