"""Parts and labor catalog provider.

MOTOR, OEM, and other vehicle-specific catalogs are licensed products.
This module ships a mock provider so the estimator can be wired now and a
licensed provider can be dropped in later without changing the estimate UI.
"""

from __future__ import annotations

from typing import Protocol


SUBPARTS = {
    "front_bumper": ["Cover", "Reinforcement", "Absorber", "Bracket", "Lower valance"],
    "grille": ["Shell", "Insert", "Emblem", "Retainer"],
    "hood": ["Skin", "Insulation", "Latch", "Hinge"],
    "fender": ["Outer panel", "Liner", "Bracket", "Molding"],
    "front_door": ["Shell", "Glass", "Regulator", "Hinge", "Handle"],
    "rear_door": ["Shell", "Glass", "Regulator", "Hinge", "Handle"],
    "roof": ["Skin", "Bow", "Drip molding", "Headliner clip"],
    "trunk": ["Lid", "Latch", "Striker", "Weatherstrip"],
    "quarter": ["Outer panel", "Wheelhouse", "Brace", "Molding"],
    "rear_body": ["Panel", "Reinforcement", "Seal"],
    "rear_bumper": ["Cover", "Reinforcement", "Absorber", "Bracket"],
    "headlamps": ["Housing", "Lens", "Bulb", "Bracket"],
    "tail_lamps": ["Housing", "Lens", "Gasket", "Clip"],
    "glass": ["Glass", "Molding", "Urethane", "Clip"],
    "mirrors": ["Glass", "Cover", "Motor", "Bracket"],
    "wheels": ["Wheel", "Center cap", "Weight", "Sensor"],
}


class PartSuggestion:
    def __init__(self, *, name: str, part_number: str, part_type: str, price_cents: int, body_hours: str, refinish_hours: str, notes: str):
        self.name = name
        self.part_number = part_number
        self.part_type = part_type
        self.price_cents = price_cents
        self.body_hours = body_hours
        self.refinish_hours = refinish_hours
        self.notes = notes

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "part_number": self.part_number,
            "part_type": self.part_type,
            "price_cents": self.price_cents,
            "body_hours": self.body_hours,
            "refinish_hours": self.refinish_hours,
            "notes": self.notes,
        }


class PartsCatalogProvider(Protocol):
    name: str
    licensed: bool

    def lookup(self, *, area: str, body_style: str = "", vin: str = "", year: str = "", make: str = "", model: str = "") -> list[dict]:
        ...


def _family(area: str) -> str:
    key = str(area or "").lower()
    for prefix in (
        "front_bumper", "rear_bumper", "grille", "hood", "fender", "front_door", "rear_door",
        "roof", "trunk", "quarter", "rear_body", "headlamps", "tail_lamps", "glass", "mirrors", "wheels",
    ):
        if key.startswith(prefix) or prefix in key:
            return prefix
    return "front_bumper"


class MockPartsCatalog:
    """Illustrative parts only. Not vehicle-specific and not for production pricing."""

    name = "mock"
    licensed = False

    def lookup(self, *, area: str, body_style: str = "", vin: str = "", year: str = "", make: str = "", model: str = "") -> list[dict]:
        family = _family(area)
        names = SUBPARTS.get(family, SUBPARTS["front_bumper"])
        suggestions = []
        for index, name in enumerate(names, start=1):
            suggestions.append(
                PartSuggestion(
                    name=name,
                    part_number=f"MOCK-{family.upper()}-{index:02d}",
                    part_type="Aftermarket",
                    price_cents=0,
                    body_hours="0.0" if family in {"glass", "wheels"} else "1.0" if index == 1 else "0.3",
                    refinish_hours="0.0" if family in {"glass", "wheels", "headlamps", "tail_lamps"} else "1.5" if index == 1 else "0.0",
                    notes="Mock catalog. Replace with a licensed MOTOR or OEM provider before production pricing.",
                ).as_dict()
            )
        return suggestions


def get_parts_catalog() -> PartsCatalogProvider:
    """Return the active catalog. Swap this factory when a licensed provider is configured."""
    return MockPartsCatalog()
