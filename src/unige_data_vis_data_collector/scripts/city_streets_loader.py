from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from unige_data_vis_data_collector.city_streets.overpass_service import (
    OverpassCityStreetsService,
)

logging.basicConfig(level=logging.INFO)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="city_streets_loader")
    p.add_argument("city", type=str, help="City name, e.g. 'Nyon'")
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON file path (default: out/city_streets_<city>.jsonl)",
    )
    p.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Overpass query batch size (default: %(default)s)",
    )
    p.add_argument(
        "--endpoint",
        type=str,
        default=None,
        help="Custom Overpass API endpoint (default: official overpass-turbo)",
    )
    return p.parse_args(argv)


def _default_output_path(city: str) -> Path:
    safe_city = city.replace(" ", "_")
    return Path("out") / f"city_streets_{safe_city}.jsonl"


def _loaded_ids(filename: str) -> list[str]:
    p_out = Path(filename)
    if not p_out.exists():
        return []
    with open(p_out, "r") as f:
        return [json.loads(line)["id"] for line in f.readlines()]


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        for city in args.city.split(","):
            logging.info("Loading city segments for %s", city)
            output = args.output or _default_output_path(city)
            service = OverpassCityStreetsService(endpoint=args.endpoint)
            with open(output, "a", encoding="utf-8") as f:
                for s in service.load_city_segments(city, batch_size=args.batch_size, exclude_ids=_loaded_ids(output)):
                    f.write(json.dumps(s, ensure_ascii=False) + "\n")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    os.environ["REQUESTS_CA_BUNDLE"] = "/Users/amasselot/zscaler/zscaler-ca-bundle.pem"
    os.environ["SSL_CERT_FILE"] = "/Users/amasselot/zscaler/zscaler-ca-bundle.pem"
    try:
        raise SystemExit(main())
    except SystemExit as e:
        sys.exit(e.code)
