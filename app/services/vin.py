"""VIN validation and NHTSA vPIC decode.

Check digit follows ISO 3779 / 49 CFR 565. NHTSA is a free decoder for year,
make, model and body description. It is not a licensed parts catalog.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Callable

VIN_LENGTH = 17
VIN_TRANSLITERATION = {
    **{str(digit): digit for digit in range(10)},
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8,
    "J": 1, "K": 2, "L": 3, "M": 4, "N": 5, "P": 7, "R": 9,
    "S": 2, "T": 3, "U": 4, "V": 5, "W": 6, "X": 7, "Y": 8, "Z": 9,
}
VIN_WEIGHTS = (8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2)
NHTSA_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"


def normalize_vin(value: str | None) -> str:
    return "".join(ch for ch in str(value or "").upper() if ch.isalnum())


def validate_vin(value: str | None) -> dict:
    vin = normalize_vin(value)
    errors: list[str] = []
    warnings: list[str] = []
    if len(vin) != VIN_LENGTH:
        errors.append(f"VIN must be {VIN_LENGTH} characters.")
    if any(ch in vin for ch in ("I", "O", "Q")):
        errors.append("VIN cannot contain I, O, or Q.")
    if any(ch not in VIN_TRANSLITERATION for ch in vin):
        errors.append("VIN contains a character that is not allowed.")

    check_ok = False
    expected = ""
    if not errors and len(vin) == VIN_LENGTH:
        total = 0
        for index, char in enumerate(vin):
            total += VIN_TRANSLITERATION[char] * VIN_WEIGHTS[index]
        remainder = total % 11
        expected = "X" if remainder == 10 else str(remainder)
        check_ok = vin[8] == expected
        if not check_ok:
            warnings.append(
                f"Check digit does not match (position 9 is {vin[8]}, expected {expected}). "
                "You can still decode and edit the vehicle, but confirm the VIN."
            )

    return {
        "vin": vin,
        "valid_format": not errors,
        "check_digit_ok": check_ok,
        "expected_check_digit": expected,
        "errors": errors,
        "warnings": warnings,
    }


def body_style_from_vpic(body_class: str | None, doors) -> str:
    text = str(body_class or "").lower()
    door_count = 0
    try:
        door_count = int(str(doors or "0").split(".")[0] or 0)
    except ValueError:
        door_count = 0
    if any(token in text for token in ("pickup", "truck", "chassis cab")):
        return "pickup"
    if "van" in text:
        return "van"
    if any(token in text for token in ("sport utility", "suv", "crossover", "hatch", "wagon", "mpv")):
        return "suv"
    if any(token in text for token in ("coupe", "convertible", "roadster")) or door_count == 2:
        return "coupe"
    return "sedan"


def _http_get(url: str, timeout: float = 8.0) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "FlagTech/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("Unexpected decoder response")
    return parsed


def decode_vin(value: str | None, *, fetcher: Callable[[str], dict] | None = None, timeout: float = 8.0) -> dict:
    validation = validate_vin(value)
    result = {
        "vin": validation["vin"],
        "validation": validation,
        "vehicle": None,
        "decoded": False,
        "error": None,
    }
    if not validation["valid_format"]:
        result["error"] = " ".join(validation["errors"])
        return result

    fetch = fetcher or (lambda url: _http_get(url, timeout=timeout))
    url = NHTSA_URL.format(vin=validation["vin"])
    try:
        payload = fetch(url)
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        result["error"] = "Vehicle decoder is unavailable. Enter the vehicle manually."
        result["decoder_detail"] = str(exc)
        return result

    rows = payload.get("Results") if isinstance(payload, dict) else None
    row = rows[0] if isinstance(rows, list) and rows else {}
    if not isinstance(row, dict):
        row = {}
    make = str(row.get("Make") or "").strip()
    model = str(row.get("Model") or "").strip()
    if not make and not model:
        message = str(row.get("ErrorText") or "").strip() or "No vehicle was returned for this VIN."
        result["error"] = message
        return result

    doors_raw = str(row.get("Doors") or "").strip()
    engine_bits = [
        str(row.get("DisplacementL") or "").strip(),
        str(row.get("EngineCylinders") or "").strip(),
        str(row.get("EngineModel") or "").strip(),
        str(row.get("FuelTypePrimary") or "").strip(),
    ]
    engine = " ".join(bit for bit in engine_bits if bit and bit not in {"0", "0.0"})
    if str(row.get("EngineCylinders") or "").strip():
        cylinders = str(row.get("EngineCylinders") or "").strip()
        displacement = str(row.get("DisplacementL") or "").strip()
        engine = " ".join(
            part
            for part in (
                f"{displacement}L" if displacement else "",
                f"{cylinders}-cyl" if cylinders else "",
                str(row.get("EngineModel") or "").strip(),
                str(row.get("FuelTypePrimary") or "").strip(),
            )
            if part
        )
    vehicle = {
        "year": str(row.get("ModelYear") or "").strip(),
        "make": make.title() if make.isupper() else make,
        "model": model,
        "trim": str(row.get("Trim") or row.get("Series") or "").strip(),
        "body_class": str(row.get("BodyClass") or "").strip(),
        "doors": doors_raw,
        "drive": str(row.get("DriveType") or "").strip(),
        "engine": engine.strip(),
        "body_style": body_style_from_vpic(row.get("BodyClass"), doors_raw),
    }
    result["vehicle"] = vehicle
    result["decoded"] = True
    return result
