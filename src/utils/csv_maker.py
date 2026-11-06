# Makes CSV files from various data sources
import csv
from pathlib import Path
from typing import Any

def json_to_csv(
    json_data: dict[str, Any] | list[dict[str, Any]],
    csv_file_path: str | Path,
    fieldnames: list[str] | None = None,
) -> Path:
    """Écrit un objet JSON ou une liste d'objets comme lignes dans un CSV."""
    csv_file_path = Path(csv_file_path)
    rows = json_data if isinstance(json_data, list) else [json_data]

    if fieldnames is None:
        if not rows:
            raise ValueError("Impossible de déduire les colonnes d'une liste vide.")
        fieldnames = list(rows[0].keys())

    with csv_file_path.open('w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return csv_file_path