from typing import Iterable

class DuplicateCodeError (ValueError):
    """Raised when a code is duplicated in a CSV file."""
    def __init__(self, code: str, first_line: int, duplicate_line: int) -> None:
        self.code = code
        self.first_line = first_line
        self.duplicate_line = duplicate_line

        super().__init__(
            f"Le code {code!r} apparaît aux lignes "
            f"{first_line} et {duplicate_line}."
        )

class InvalidFieldsError (ValueError):
    """Raised when a CSV file has invalid fields."""
    def __init__(self, valid_fields: list[str], invalid_fields: list[str]) -> None:
        
        self.invalid_field = invalid_fields
        
        super().__init__(
            f"Le CSV a des champs invalides: {invalid_fields} "
            f"ne sont pas dans {valid_fields}."
        )
        