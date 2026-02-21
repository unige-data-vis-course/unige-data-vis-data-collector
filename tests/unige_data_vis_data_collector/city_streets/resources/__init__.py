import json
import os
from typing import Optional


def mock_segments_json(line_number: Optional[int]) -> dict | list[dict]:
    filename = os.path.join(os.path.dirname(__file__), "overpass_segments.jsonl")
    ret = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = json.loads(line)
            ret.append(line)
    if line_number is not None:
        return ret[line_number]
    return ret
