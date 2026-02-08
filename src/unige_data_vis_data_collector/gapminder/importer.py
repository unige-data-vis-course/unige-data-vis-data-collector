from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd
from pandas import DataFrame

from .models import GapminderConcept, GapminderConcepts
import csv


class GapminderImporter:
    source_dir: Path
    _concepts: GapminderConcepts | None = None

    def __init__(self,
                 source_dir: Union[str, Path] = "data/ddf--gapminder--fasttrack/"
                 ):
        self.source_dir = self._normalize_source_dir(source_dir)

    @property
    def concepts(self) -> GapminderConcepts:
        if self._concepts is None:
            path = self._resolve_concepts_path()
            rows = self._read_concepts_csv(path)
            self._concepts = GapminderConcepts([self._row_to_concept(r) for r in rows])
        return self._concepts

    def by_country_data(self, concept_id: str) -> DataFrame:
        return pd.read_csv(self.by_country_csv_filename(concept_id))

    def by_country_csv_filename(self, concept_id: str) -> Path:
        return self.source_dir / "countries_etc_datapoints" / f"ddf--datapoints--{concept_id}--by--country--time.csv"

    @staticmethod
    def _normalize_source_dir(source_dir: Union[str, Path]) -> Path:
        return source_dir if isinstance(source_dir, Path) else Path(source_dir)

    def _resolve_concepts_path(self) -> Path:
        primary = self.source_dir / "ddf--concepts.csv"
        if primary.exists():
            return primary
        raise FileNotFoundError(f"Concepts CSV not found in {primary}")

    def country_def_file(self) -> Path:
        return self.source_dir / "ddf--entities--geo--country.csv"

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
