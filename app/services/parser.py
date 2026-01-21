import re
from typing import List
from app.models.estimate import LineItem

EXPECTED_HEADERS = [
    "line", "oper", "description", "part", "qty",
    "extended", "labor", "paint"
]

LABOR_PATTERN = re.compile(r"^\d+(\.\d+)?$|^incl$", re.IGNORECASE)


def find_headers(page):
    header_positions = {}

    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip().lower()
                for header in EXPECTED_HEADERS:
                    if text.startswith(header):
                        header_positions[header] = span["bbox"][0]

    return dict(sorted(header_positions.items(), key=lambda x: x[1]))


def assign_column(x, header_positions):
    headers = list(header_positions.items())
    for i, (header, x_pos) in enumerate(headers):
        if i == len(headers) - 1:
            return header
        next_x = headers[i+1][1]
        if x_pos <= x < next_x:
            return header
    return None


def extract_repair_lines(page, header_positions):
    results = []

    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue

        for line in block["lines"]:
            spans = line["spans"]
            if not spans:
                continue

            # Must start with a line number
            first = spans[0]["text"].strip()
            if not first.isdigit():
                continue

            row = {h: "" for h in header_positions}

            for span in spans:
                text = span["text"].strip()
                x = span["bbox"][0]
                col = assign_column(x, header_positions)
                if col:
                    row[col] = (row[col] + " " + text).strip()

            results.append(row)

    return results


def filter_labor_lines(lines):
    return [
        row for row in lines
        if LABOR_PATTERN.match(row.get("labor", ""))
    ]


def parse_estimate_pdf(doc):
    page = doc[0]  # CCC repair lines are on page 1

    headers = find_headers(page)
    repair_lines = extract_repair_lines(page, headers)
    labor_lines = filter_labor_lines(repair_lines)

    return labor_lines


def parse_estimate_text(text: str) -> List[LineItem]:
    """Parse estimate text and return a list of LineItem objects."""
    items = []
    
    # Split text into lines
    lines = text.split('\n')
    
    for line_text in lines:
        line_text = line_text.strip()
        if not line_text:
            continue
            
        # Try to match lines that start with a number (line number)
        # Basic pattern: line_num operation description labor paint
        match = re.match(r'^(\d+)\s+(.+)', line_text)
        if match:
            line_num = int(match.group(1))
            rest = match.group(2).strip()
            
            # Try to extract labor and paint values (numbers at the end)
            # Look for patterns like "1.5" or "2.0" at the end
            labor = None
            paint = None
            operation = None
            description = rest
            
            # Extract numbers from the end of the line
            numbers = re.findall(r'\d+\.\d+|\d+', rest)
            if numbers:
                # Last number could be paint, second to last could be labor
                if len(numbers) >= 1:
                    try:
                        labor = float(numbers[-1])
                    except:
                        pass
                if len(numbers) >= 2:
                    try:
                        paint = float(numbers[-2])
                        # Remove paint from the description
                        description = rest
                    except:
                        pass
            
            items.append(LineItem(
                line=line_num,
                operation=operation,
                description=description,
                labor=labor,
                paint=paint
            ))
    
    return items