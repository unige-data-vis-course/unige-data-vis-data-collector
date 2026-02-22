import json
import os
from enum import Enum
from typing import Any, Iterable, List, Optional

from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import TypeAdapter
from pydantic import field_validator


class Gender(str, Enum):
    NEUTRAL = "NEUTRAL"
    MALE = "MALE"
    FEMALE = "FEMALE"

    @classmethod
    def _missing_(cls, value: object):
        if not isinstance(value, str):
            return None
        s = value.strip().lower()
        mapping = {
            "male": cls.MALE,
            "m": cls.MALE,
            "man": cls.MALE,
            "masculine": cls.MALE,
            "female": cls.FEMALE,
            "f": cls.FEMALE,
            "woman": cls.FEMALE,
            "feminine": cls.FEMALE,
            "neutral": cls.NEUTRAL,
            "n": cls.NEUTRAL,
            "unknown": cls.NEUTRAL,
            "other": cls.NEUTRAL,
            "non-binary": cls.NEUTRAL,
            "nonbinary": cls.NEUTRAL,
            "nb": cls.NEUTRAL,
        }
        return mapping.get(s)


class StreetPeopleGenderInferenceItem(BaseModel):
    street_name: str
    is_people: bool
    gender: Optional[Gender] = None

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("gender", mode="after")
    def _enforce_none_when_not_people(cls, v: Optional[Gender], info):
        data = info.data if hasattr(info, "data") else {}
        if data.get("is_people") is False:
            return None
        return v


class PeopleGenderInferenceService:
    def __init__(self, llm: Any):
        # llm must expose an "invoke" method that takes a prompt string and returns either
        # a string (JSON) or an object with a "content" field containing the JSON string.
        self._llm = llm
        self._list_adapter: TypeAdapter[List[StreetPeopleGenderInferenceItem]] = TypeAdapter(
            List[StreetPeopleGenderInferenceItem]
        )

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
        text = self._coerce_to_text(raw)
        ret = self._parse_items_from_text(text)
        return ret

    def _build_prompt(self, names: List[str]) -> str:
        schema_json = self._pydantic_schema_json()
        format_instructions = self._format_instructions_text()
        example = [
            {"street_name": "Avenue Marie Curie", "is_people": True, "gender": "FEMALE"},
            {"street_name": "Rue du Lac", "is_people": False, "gender": None},
        ]
        return (
            f"{format_instructions}\n\n"
            f"Pydantic JSON Schema for one item (StreetPeopleGenderInferenceItem):\n{schema_json}\n\n"
            f"Street names (preserve order and exact spelling): {json.dumps(names, ensure_ascii=False)}\n\n"
            f"Example output (array of items): {json.dumps(example, ensure_ascii=False)}\n\n"
            f"Respond with the JSON array ONLY. No prose, no code fences."
        )

    def _pydantic_schema_json(self) -> str:
        schema = StreetPeopleGenderInferenceItem.model_json_schema()
        return json.dumps(schema, ensure_ascii=False)

    def _format_instructions_text(self) -> str:
        return (
            "You are a precise classifier. For each input street name, decide if it refers to a person. "
            "If it does, set gender to one of: NEUTRAL, MALE, FEMALE. If not a person, set gender to null. "
            "Output MUST be a JSON array of StreetPeopleGenderInferenceItem objects as defined by the Pydantic schema. "
            "Maintain the same order as input and keep street_name exactly as given."
        )

    def _invoke_llm(self, prompt: str) -> Any:
        try:
            return self._llm.invoke(prompt)
        except TypeError:
            return self._llm(prompt)

    def _coerce_to_text(self, result: Any) -> str:
        if result is None:
            raise ValueError("LLM returned no content")
        if isinstance(result, str):
            return result.strip()
        text = getattr(result, "content", None)
        if text is None and hasattr(result, "dict"):
            try:
                text = result.dict().get("content")
            except Exception:
                text = None
        if text is None:
            try:
                text = json.dumps(result)
            except Exception as e:
                raise ValueError("Unrecognized LLM result format") from e
        return str(text).strip()

    def _extract_json_array(self, text: str) -> str:
        t = text.strip()
        if t.startswith("```") and t.endswith("```"):
            t = t.strip("`")
        if t.lstrip().startswith("[") and t.rstrip().endswith("]"):
            return t
        start = t.find("[")
        end = t.rfind("]")
        if start != -1 and end != -1 and end > start:
            return t[start: end + 1]
        raise ValueError("No JSON array found in LLM output")

    def _parse_items_from_text(self, text: str) -> List[StreetPeopleGenderInferenceItem]:
        array_json = self._extract_json_array(text)
        return self._list_adapter.validate_json(array_json)
