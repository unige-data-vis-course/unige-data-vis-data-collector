from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


class CannotParseDateException(Exception):
    def __init__(self, date_str: str, formats: list[str]):
        super().__init__(f"Cannot parse date {date_str} with any of the following formats: {formats}")


@dataclass(frozen=True)
class GapminderConcept:
    id: str
    type: str
    updated_at: str
    name: str
    description_short: str
    description: str

    @property
    def predicted_since_year(self) -> Optional[int]:
        formats = [
            "%Y %B %d",
            "%B %d %Y",
            "%B %d, %Y",
            "%B %d,%Y"
        ]
        if not self.updated_at:
            return None
        for fmt in formats:
            try:
                return datetime.strptime(self.updated_at, fmt).year
            except ValueError:
                continue
        raise CannotParseDateException(self.updated_at, formats)

    def __str__(self):
        pred = f"[pred>={self.predicted_since_year}]" if self.predicted_since_year else "[no prediction]"

        return f"{self.id} ({pred}): {self.name}"


class CannotFindConceptByIdException(Exception):
    def __init__(self, id: str):
        super().__init__(f"Cannot find concept with id {id}")


class MultipleFindConceptByIdException(Exception):
    def __init__(self, id: str):
        super().__init__(f"Cannot find concept with id {id}")


class GapminderConcepts(list[GapminderConcept]):
    def by_id(self, id: str) -> GapminderConcept:
        cs = [c for c in self if c.id == id]
        if len(cs) == 0:
            raise CannotFindConceptByIdException(id)
        if len(cs) > 1:
            raise MultipleFindConceptByIdException(id)
        return cs[0]


__all__ = [
    "GapminderConcept",
    "GapminderConcepts",
]
