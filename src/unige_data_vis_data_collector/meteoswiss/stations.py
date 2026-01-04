from __future__ import annotations

import os
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import List

import pandas as pd
import requests

# Base folder where raw metadata CSVs live (relative to project root when installed in editable mode)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Default remote CSV locations from MeteoSwiss OGD
SMN_STATIONS_URL = (
    "https://data.geo.admin.ch/ch.meteoschweiz.ogd-smn/ogd-smn_meta_stations.csv"
)
PRECIP_STATIONS_URL = (
    "https://data.geo.admin.ch/ch.meteoschweiz.ogd-smn-precip/ogd-smn-precip_meta_stations.csv"
)


@dataclass
class Station:
    abbr: str
    name: str
    canton: str
    wigos_id: str | None
    lat: float | None
    lon: float | None
    height_masl: float | None
    has_observations_smn: bool
    has_observations_precip: bool


def _read_csv_local(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=';', encoding='latin1')


def _read_csv_remote(url: str, timeout: int = 20) -> pd.DataFrame:
    resp = requests.get(url, timeout=timeout, verify=_get_requests_verify())
    resp.raise_for_status()
    return pd.read_csv(BytesIO(resp.content), sep=';', encoding='latin1')


def _get_requests_verify():
    env = os.getenv("REQUESTS_CA_BUNDLE") or os.getenv("METEOSWISS_CA_BUNDLE")
    if env and Path(env).exists():
        return env
    default = PROJECT_ROOT / "secrets" / "zscaler-bundle-ca.pem"
    return str(default) if default.exists() else True


def load_smn_stations(path: Path | str | None = None) -> pd.DataFrame:
    if path is None:
        return _read_csv_remote(SMN_STATIONS_URL)
    if isinstance(path, str) and path.startswith(("http://", "https://")):
        return _read_csv_remote(path)
    return _read_csv_local(Path(path))


def load_precip_stations(path: Path | str | None = None) -> pd.DataFrame:
    if path is None:
        return _read_csv_remote(PRECIP_STATIONS_URL)
    if isinstance(path, str) and path.startswith(("http://", "https://")):
        return _read_csv_remote(path)
    return _read_csv_local(Path(path))


def _df_to_station_list(df: pd.DataFrame, precip: bool = False) -> List[Station]:
    rows: List[Station] = []
    for _, r in df.iterrows():
        rows.append(
            Station(
                abbr=str(r.get('station_abbr')).strip(),
                name=str(r.get('station_name')).strip(),
                canton=str(r.get('station_canton')).strip(),
                wigos_id=(str(r.get('station_wigos_id')).strip() if pd.notna(r.get('station_wigos_id')) else None),
                lat=float(r.get('station_coordinates_wgs84_lat')) if pd.notna(r.get('station_coordinates_wgs84_lat')) else None,
                lon=float(r.get('station_coordinates_wgs84_lon')) if pd.notna(r.get('station_coordinates_wgs84_lon')) else None,
                height_masl=float(r.get('station_height_masl')) if pd.notna(r.get('station_height_masl')) else None,
                has_observations_smn=not precip,
                has_observations_precip=precip,
            )
        )
    return rows


def get_all_stations(
    smn_path: Path | str | None = None,
    precip_path: Path | str | None = None,
) -> List[Station]:
    smn_df = load_smn_stations(smn_path)
    precip_df = load_precip_stations(precip_path)

    smn_list = _df_to_station_list(smn_df, precip=False)
    precip_list = _df_to_station_list(precip_df, precip=True)

    by_abbr: dict[str, Station] = {}
    for st in smn_list:
        by_abbr[st.abbr] = st

    for st in precip_list:
        if st.abbr in by_abbr:
            # Merge flags
            existing = by_abbr[st.abbr]
            by_abbr[st.abbr] = Station(
                abbr=existing.abbr,
                name=existing.name or st.name,
                canton=existing.canton or st.canton,
                wigos_id=existing.wigos_id or st.wigos_id,
                lat=existing.lat if existing.lat is not None else st.lat,
                lon=existing.lon if existing.lon is not None else st.lon,
                height_masl=existing.height_masl if existing.height_masl is not None else st.height_masl,
                has_observations_smn=True,
                has_observations_precip=True,
            )
        else:
            by_abbr[st.abbr] = st

    return list(by_abbr.values())
