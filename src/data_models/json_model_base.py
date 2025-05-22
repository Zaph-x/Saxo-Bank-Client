from abc import ABC
import json
import jsonschema
from humps import camelize, decamelize


class JsonModelBase(ABC):
    __schema__: dict

    def to_json(self) -> str:
        __dict = self.__dict__
        for key, value in __dict.items():
            if isinstance(value, JsonModelBase):
                __dict[key] = __dict[key].to_json()
        return json.dumps(
            camelize(
                __dict,
            ),
        )

    @classmethod
    def from_json(cls, json_data: str | dict):
        cls.validate_json(json_data)

        if isinstance(json_data, dict):
            return cls(
                **decamelize(
                    json_data,
                ),
            )

        return cls(
            **decamelize(
                json.loads(json_data),
            ),
        )

    @classmethod
    def validate_json(cls, json_str: str | dict):
        if isinstance(json_str, dict):
            jsonschema.validate(
                json_str,
                cls.__schema__,
            )
            return

        jsonschema.validate(
            json.loads(json_str),
            cls.__schema__,
        )
