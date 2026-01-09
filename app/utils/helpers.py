import re

def clean_price(value: str) -> float | None:
    """Convert price string to float, removing commas and handling empty values."""
    if not value or value.lower() == "incl.":
        return None
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None

def clean_quantity(value: str) -> int | None:
    """Convert quantity string to int, handling empty values."""
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None

def clean_float(value: str) -> float | None:
    """Convert labor/paint string to float, handling 'Incl.' and empty values."""
    if not value or value.lower() == "incl.":
        return None
    try:
        return float(value)
    except ValueError:
        return None

def normalize_operation(op: str) -> str | None:
    """Standardize operation codes like 'Repl', 'R&I', 'O/H'."""
    op = op.strip().upper()
    if op in ["REPL", "R&I", "O/H", "<>"]:
        return op
    return None

def strip_line_artifacts(line: str) -> str:
    """Remove leading/trailing pipes and whitespace from a line."""
    return line.strip().strip("|").strip()

def is_estimate_line(line: str) -> bool:
    """Check if a line looks like a valid estimate row (starts with a line number)."""
    # Accept lines that start with a number (with or without surrounding pipes)
    return bool(re.match(r"^\s*\d+\b", line))

def safe_split(line: str, delimiter: str = "|") -> list[str]:
    """Split a line safely by delimiter and strip each part."""
    return [part.strip() for part in line.split(delimiter)]