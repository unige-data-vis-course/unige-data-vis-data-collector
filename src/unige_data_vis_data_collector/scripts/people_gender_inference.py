import argparse
import json
import sys
from typing import List

from unige_data_vis_data_collector.city_streets.people_gender_inference_service import (
    PeopleGenderInferenceService,
)
from unige_data_vis_data_collector.scripts import setup_logging

setup_logging()


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Infer if street names refer to a person and output gender (NEUTRAL|MALE|FEMALE).\n"
            "Prints strictly a JSON array with fields street_name, is_people, gender."
        )
    )
    p.add_argument(
        "names",
        nargs="+",
        help="Street names to analyze (provide one or more)",
    )
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    service = PeopleGenderInferenceService.from_azure_env()
    items = service.infer(args.names)
    # Strict JSON array only
    print(
        json.dumps([item.dict() for item in items], ensure_ascii=False),
        end="",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
