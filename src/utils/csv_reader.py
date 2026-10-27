from collections.abc import Iterator
import csv
from src.error_types import DuplicateCodeError, InvalidFieldsError
from pathlib import Path

# File paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_READ_FROM = PROJECT_ROOT / "data" / "catalogue.csv"
DEMAND_READ_FROM = PROJECT_ROOT / "data" / "demande.csv"

# fieldnames for 
CATALOG_FIELDS = ["code", "name", "price"]
DEMAND_FIELDS = ["code", "quantity"]

def __validate_fields(csv_reader: csv.DictReader, fields: list[str]) -> None:
    actual_fields = csv_reader.fieldnames

    if actual_fields is None or list(actual_fields) != fields:
        raise InvalidFieldsError(
            fields,
            list(actual_fields) if actual_fields is not None else [],
        )

def __validate_length(rows: dict[str, dict[str, str]]) -> None:
    """Validates if the length of the CSV is correct."""
    if len(rows) < 1:
        raise ValueError("The CSV must have at least 2 lines (1 for the header the other for at least one line of data).")

def _index_by_code(rows: Iterator[dict[str, str]]) -> dict[str, dict[str, str]]:
    """Indexe les lignes CSV par code et refuse les codes en double."""
    indexed_rows = {}
    line_numbers = {}

    for line_number, row in enumerate(rows, start=2):
        code = row["code"]

        if code in indexed_rows:
            raise DuplicateCodeError(code, line_numbers[code], line_number)

        indexed_rows[code] = row
        line_numbers[code] = line_number
    
    __validate_length(indexed_rows)

    return indexed_rows

def read_catalogue(file_path: Path = CATALOG_READ_FROM) -> dict[str, dict[str, str]]:
    """Returns the catalogue indexed by code."""    
    with file_path.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        
        __validate_fields(reader, CATALOG_FIELDS)        
        
        return _index_by_code(reader)

def read_demand(file_path: Path = DEMAND_READ_FROM) -> dict[str, dict[str, str]]:
    """Returns the demand indexed by code."""
    with file_path.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)        
        
        # validations
        __validate_fields(reader, DEMAND_FIELDS)
        
        return _index_by_code(reader)
            