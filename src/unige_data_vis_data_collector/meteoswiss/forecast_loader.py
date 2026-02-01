import datetime
import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

import pandas as pd
import requests

STAC_API_BASE = "https://data.geo.admin.ch/api/stac/v1"
COLLECTION_ID = "ch.meteoschweiz.ogd-local-forecasting"


def _parse_timestamp(ts: str) -> datetime:
    return datetime.datetime.strptime(ts, "%Y%m%d%H%M").replace(tzinfo=datetime.UTC)


def _parse_asset_name(name: str) -> tuple[str, datetime]:
    return (
        name.split(".")[3],
        _parse_timestamp(name.split(".")[2])
    )


@dataclass(frozen=True)
class ForecastAsset:
    type: str
    href: str
    timestamp: datetime
    feature_name: str

    @staticmethod
    def from_dict(d: dict, timestamp: datetime, feature: str) -> "ForecastAsset":
        return ForecastAsset(
            type=d["type"],
            href=d["href"],
            timestamp=timestamp,
            feature_name=feature
        )


@dataclass(frozen=True)
class ForecastAssetCollection:
    assets: list[ForecastAsset]

    @staticmethod
    def from_stac_items(payload: dict) -> "ForecastAssetCollection":
        ret = []
        for item_name, item_payload in payload.items():
            feature, timestamp = _parse_asset_name(item_name)
            ret.append(ForecastAsset.from_dict(item_payload, timestamp, feature))
        return ForecastAssetCollection(ret)

    def __len__(self):
        return len(self.assets)

    def __iter__(self):
        return iter(self.assets)

    def filter_by_features(self, features: str | list[str]) -> "ForecastAssetCollection":
        if isinstance(features, str):
            features = {features}
        else:
            features = set(features)
        return ForecastAssetCollection([asset for asset in self.assets if asset.feature_name in features])


@dataclass(frozen=True)
class ForecastElement:
    forecasting_timestamp: datetime
    forecast_timestamp: datetime
    point_id: int
    point_type_id: str
    value: Optional[float]
    feature_name: str


@dataclass(frozen=True)
class ForecastCollection:
    elements: list[ForecastElement]

    def __len__(self):
        return len(self.elements)

    def __add__(self, other: "ForecastCollection") -> "ForecastCollection":
        return ForecastCollection(self.elements + other.elements)

    def starts_at(self) -> Optional[datetime]:
        if len(self) == 0:
            return None
        return min(asset.forecasting_timestamp for asset in self.elements)

    def ends_at(self) -> Optional[datetime]:
        if len(self) == 0:
            return None
        return max(asset.forecasting_timestamp for asset in self.elements)

    def __iter__(self):
        return iter(self.elements)


class ForecastLoader:
    def __init__(self):
        self.items_url = f"{STAC_API_BASE}/collections/{COLLECTION_ID}/items"

    def load_all_forecast_elements(self, features: str | list[str] | None) -> ForecastCollection:
        assets = self.load_stac_items().filter_by_features(features)
        if not features:
            assets = assets.filter_by_features(features)
        fc = ForecastCollection([])
        for asset in assets:
            fc += self.load_forecast_elements(asset)
        return fc

    def load_stac_items(self) -> ForecastAssetCollection:
        logging.info(f"Loading STAC items... {self.items_url}")
        response = requests.get(self.items_url)
        response.raise_for_status()
        response_payload = response.json()

        assets_payload = {}
        for ft in response_payload["features"]:
            assets_payload = {**ft["assets"], **assets_payload}

        return ForecastAssetCollection.from_stac_items(assets_payload)

    @staticmethod
    def load_forecast_elements(asset: ForecastAsset) -> ForecastCollection:
        logging.info(f"Loading forecast elements for {asset.href}")
        response = requests.get(asset.href, timeout=30)
        response.raise_for_status()
        df = pd.read_csv(BytesIO(response.content), sep=';')
        rows = df.to_dict(orient='records')
        return ForecastCollection(elements=[
            ForecastElement(
                forecasting_timestamp=asset.timestamp,
                forecast_timestamp=datetime.datetime.strptime(str(row['Date']), "%Y%m%d%H%M%S").replace(tzinfo=datetime.UTC),
                point_id=row['point_id'],
                point_type_id=row['point_type_id'],
                value=row[asset.feature_name],
                feature_name=asset.feature_name
            ) for row in rows
        ])
