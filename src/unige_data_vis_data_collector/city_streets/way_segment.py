import logging
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class Point:
    lat: float
    lon: float

    def __str__(self):
        return f"({self.lat}, {self.lon})"


@dataclass(frozen=True, slots=True)
class Path:
    points: list[Point]

    def __len__(self):
        return len(self.points)

    def __str__(self):
        return "-".join([str(p) for p in self.points])


@dataclass(frozen=True, slots=True)
class WaySegment:
    id: int
    path: Path
    tags: dict[str, str]

    @staticmethod
    def deserialize(obj: dict) -> "WaySegment":
        return WaySegment(
            id=obj["id"],
            path=Path(points=[Point(lat=o["lat"], lon=o["lon"]) for o in obj["geometry"]]),
            tags=obj["tags"]
        )

    @property
    def name(self) -> str:
        return self.tags.get("name")

    @property
    def nb_lanes(self) -> Optional[int]:
        if "lanes" not in self.tags:
            return None
        return int(self.tags["lanes"])

    @property
    def maxspeed(self) -> Optional[int]:
        if "maxspeed" in self.tags:
            try:
                return int(self.tags["maxspeed"])
            except ValueError:
                logging.info(f'cannot parse maxspeed {self.tags["maxspeed"]}')
                return None
        return None

    def __str__(self):
        return f"[{self.id}] {self.name} lanes:{self.nb_lanes} maxspeed:{self.maxspeed}: {self.path}"

    def __getitem__(self, i: int | slice) -> Point | list[Point]:
        return self.path.points[i]
