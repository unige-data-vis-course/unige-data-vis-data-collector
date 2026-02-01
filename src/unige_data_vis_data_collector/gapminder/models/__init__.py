from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class GapminderConcept:
    id: str
    type: str
    updated_at: str
    name: str
    description_short: str
    description: str


# Type alias for a collection of concepts
GapminderConcepts = List[GapminderConcept]

__all__ = [
    "GapminderConcept",
    "GapminderConcepts",
]
