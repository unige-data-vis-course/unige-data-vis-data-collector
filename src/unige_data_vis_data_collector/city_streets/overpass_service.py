import logging
from typing import Dict, List, Any, Generator

import requests

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)


class OverpassCityStreetsService:
    def __init__(self, endpoint: str | None = None):
        self.endpoint = endpoint or "https://overpass.osm.ch/api/interpreter"

    def load_city_ids(self, city_name):
        query = f"""
[out:json][timeout:1000];
relation["name"="{city_name}"]["admin_level"="8"];
map_to_area -> .ville_cible;

way["highway"]["name"](area.ville_cible);
out ids;
"""
        elements = self._fetch_batch(query)
        return [e["id"] for e in elements]

    def load_city_segments(self, city_name: str, batch_size: int = 50, exclude_ids: list[str] = []) -> Generator[Dict[str, Any], None, None]:
        all_ids = self.load_city_ids(city_name)
        exclude_ids = set(exclude_ids)
        to_load_ids = [id for id in all_ids if id not in exclude_ids]
        for i in (range(0, len(to_load_ids), batch_size)):
            print(f"{i}/{len(to_load_ids)}")
            batch_ids = to_load_ids[i:(i + batch_size)]
            query = self._build_query(city_name, batch_ids)
            elements = self._fetch_batch(query)
            if not elements:
                break
            for element in elements:
                yield element

    def _build_query(self, city_name: str, ids: list[str]) -> str:
        id_tag = ",".join([str(id) for id in ids])
        return f"""
[out:json][timeout:1000];
way(id:{id_tag});
out geom;
"""

    def _fetch_batch(self, query: str) -> List[Dict[str, Any]]:
        resp = requests.post(self.endpoint, data={"data": query}, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data.get("elements", [])
