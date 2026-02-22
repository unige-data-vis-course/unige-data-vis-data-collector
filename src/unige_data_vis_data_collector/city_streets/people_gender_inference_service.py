import json
import os
from enum import Enum
from typing import Any, Iterable, List, Optional

from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, validator


class Gender(str, Enum):
    NEUTRAL = "NEUTRAL"
    MALE = "MALE"
    FEMALE = "FEMALE"


class StreetPeopleGenderInferenceItem(BaseModel):
    street_name: str
    is_people: bool
    gender: Optional[Gender] = None

    class Config:
        use_enum_values = True

    @validator("gender", pre=True)
    def _normalize_gender(cls, v: Any) -> Any:
        if v is None:
            return None
        if isinstance(v, Gender):
            return v
        if isinstance(v, str):
            s = v.strip().lower()
            if s in {"male", "m", "man", "masculine"}:
                return Gender.MALE
            if s in {"female", "f", "woman", "feminine"}:
                return Gender.FEMALE
            if s in {"neutral", "n", "unknown", "other", "non-binary", "nonbinary", "nb"}:
                return Gender.NEUTRAL
            # Try uppercase exact match as last resort
            try:
                return Gender[s.upper()]
            except Exception:
                return None
        return None

    @validator("gender")
    def _enforce_none_when_not_people(cls, v: Optional[Gender], values: dict) -> Optional[Gender]:
        is_people = values.get("is_people")
        if is_people is False:
            return None
        return v


class PeopleGenderInferenceService:
    def __init__(self, llm: Any):
        # llm must expose an "invoke" method that takes a prompt string and returns either
        # a string (JSON) or an object with a "content" field containing the JSON string.
        self._llm = llm

    @staticmethod
    def from_azure_env() -> "PeopleGenderInferenceService":
        # Lazily import to avoid mandatory dependency at import time (tests can inject fakes)

        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", )
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not (deployment and endpoint and api_key):
            raise EnvironmentError(
                "Missing one of required env vars: AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY"
            )
        llm = AzureChatOpenAI(
            azure_deployment=deployment,
            openai_api_version=api_version,
            azure_endpoint=endpoint,
            api_key=api_key,
            temperature=0.0,
        )
        return PeopleGenderInferenceService(llm)

    def infer(self, street_names: Iterable[str]) -> List[StreetPeopleGenderInferenceItem]:
        names = [s for s in street_names]
        prompt = self._build_prompt(names)
        raw = self._invoke_llm(prompt)
        data = self._coerce_to_json_like(raw)
        ret = self._parse_items(data)
        for r in ret:
            print(r.street_name, r.is_people, r.gender)
        return ret

    def _build_prompt(self, names: List[str]) -> str:
        example = [
            {"street_name": "Avenue Marie Curie", "is_people": True, "gender": "FEMALE"},
            {"street_name": "Rue du Lac", "is_people": False, "gender": None},
        ]
        instructions = (
            "You are a precise classifier. Given street names, decide if each name refers to a person. "
            "If yes, classify gender as one of NEUTRAL, MALE, FEMALE. If not a person, set gender to null. "
            "in the output, the street names must be in the same order as the input and with the exact same value."
            "Return strictly a JSON array ONLY, no prose, following this schema: "
            "[{street_name:str, is_people:bool, gender:null|NEUTRAL|MALE|FEMALE}]."
        )
        return (
            f"{instructions}\n\n"
            f"Street names: {json.dumps(names, ensure_ascii=False)}\n\n"
            f"Example output: {json.dumps(example, ensure_ascii=False)}\n\n"
            f"Now answer with the JSON array only."
        )

    def _invoke_llm(self, prompt: str) -> Any:
        try:
            result = self._llm.invoke(prompt)
        except TypeError:
            # Some LLMs may be callable directly
            result = self._llm(prompt)
        return result

    def _coerce_to_json_like(self, result: Any) -> Any:
        if result is None:
            raise ValueError("LLM returned no content")
        if isinstance(result, str):
            text = result
        else:
            # langchain messages may have .content
            text = getattr(result, "content", None)
            if text is None and hasattr(result, "dict"):
                try:
                    text = result.dict().get("content")
                except Exception:
                    pass
            if text is None:
                # last resort: try to JSON-serialize then parse
                try:
                    text = json.dumps(result)
                except Exception:
                    raise ValueError("Unrecognized LLM result format")

        text = text.strip()
        # Remove potential code fences
        if text.startswith("```") and text.endswith("```"):
            text = text.strip("`")
        # Try parse JSON
        try:
            return json.loads(text)
        except Exception:
            # Sometimes model may wrap with prose; try to extract first JSON array
            start = text.find("[")
            end = text.rfind("]")
            if start != -1 and end != -1 and end > start:
                snippet = text[start: end + 1]
                return json.loads(snippet)
            raise

    def _parse_items(self, data: Any) -> List[StreetPeopleGenderInferenceItem]:
        if not isinstance(data, list):
            raise ValueError("Expected a JSON array of items")
        items: List[StreetPeopleGenderInferenceItem] = []
        for obj in data:
            if not isinstance(obj, dict):
                raise ValueError("Each array element must be an object")
            items.append(StreetPeopleGenderInferenceItem(**obj))
        return items
