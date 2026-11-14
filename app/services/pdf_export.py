"""Minimal text PDF writer for estimate and repair-order printouts.

No third-party PDF library is required. Output is a single-page text document.
"""

from __future__ import annotations


def _escape(text: str) -> str:
    return (
        str(text or "")
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def render_text_pdf(title: str, lines: list[str]) -> bytes:
    commands = ["BT", "/F1 16 Tf", "48 780 Td", f"({_escape(title)}) Tj", "/F1 10 Tf"]
    y_shift = -18
    for line in lines[:70]:
        commands.append(f"0 {y_shift} Td ({_escape(line)[:110]}) Tj")
        y_shift = -14
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1", "replace")
    objects = []

    def add(body: bytes) -> int:
        objects.append(body)
        return len(objects)

    add(b"<< /Type /Catalog /Pages 2 0 R >>")
    add(b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>")
    add(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>")
    add(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
    add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(body)
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects)+1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode("ascii")
    )
    return bytes(output)
