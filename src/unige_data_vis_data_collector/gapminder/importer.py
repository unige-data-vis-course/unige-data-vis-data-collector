from __future__ import annotations

from pathlib import Path
from typing import Union

from .models import GapminderConcept, GapminderConcepts
import csv


class GapminderImporter:
    def __init__(self, source_dir: Union[str, Path]):
        self.source_dir = self._normalize_source_dir(source_dir)

    @staticmethod
    def _normalize_source_dir(source_dir: Union[str, Path]) -> Path:
        return source_dir if isinstance(source_dir, Path) else Path(source_dir)

    def load_concepts(self) -> GapminderConcepts:
        path = self._resolve_concepts_path()
        rows = self._read_concepts_csv(path)
        return [self._row_to_concept(r) for r in rows]

    def _resolve_concepts_path(self) -> Path:
        primary = self.source_dir / "ddf-concepts.csv"
        fallback = self.source_dir / "ddf--concepts.csv"
        if primary.exists():
            return primary
        if fallback.exists():
            return fallback
        raise FileNotFoundError(f"Concepts CSV not found in {self.source_dir}")

    @staticmethod
    def _read_concepts_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [dict(r) for r in reader]

    @staticmethod
    def _row_to_concept(r: dict[str, str]) -> GapminderConcept:
        def gv(key: str) -> str:
            v = r.get(key, "")
            return v.strip() if isinstance(v, str) else ""

        return GapminderConcept(
            id=gv("concept"),
            type=gv("concept_type"),
            updated_at=gv("updated"),
            name=gv("name_short"),
            description_short=gv("name"),
            description=gv("description"),
        )
