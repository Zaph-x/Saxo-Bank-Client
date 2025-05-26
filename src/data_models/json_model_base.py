from abc import ABC
import json
import jsonschema
from humps import camelize, decamelize
from enum import Enum


class EnumEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return o.value
        if hasattr(o, 'to_dict'):
            return o.to_dict()
        return super().default(o)


class JsonModelBase(ABC):
    __schema__: dict

    def to_json(self) -> str:
        __dict = {}
        for key, value in self.__dict__.items():
            if isinstance(value, JsonModelBase):
                __dict[key] = json.loads(value.to_json())
            elif isinstance(value, Enum):
                __dict[key] = value.value
            else:
                __dict[key] = value
        
        # Camelize the keys (convert snake_case to camelCase)
        return json.dumps(camelize(__dict), cls=EnumEncoder)

    @classmethod
    def from_json(cls, json_data: str | dict):
        cls.validate_json(json_data)

        # Convert string to dict if needed
        if not isinstance(json_data, dict):
            json_data = json.loads(json_data)
            
        # Check if the class constructor parameters are in camelCase or snake_case
        # Get the first __init__ parameter name to check its format
        import inspect
        params = list(inspect.signature(cls.__init__).parameters.keys())
        if len(params) > 1:  # Skip 'self'
            first_param = params[1]  # First param after 'self'
            if first_param[0].isupper():  # If param starts with uppercase, it's camelCase
                # Don't decamelize for classes with camelCase parameters
                # Ensure all keys are strings
                cleaned_json_data = {str(k): v for k, v in json_data.items()}
                return cls(**cleaned_json_data)
            
        # Normal case: convert camelCase to snake_case for other classes
        return cls(**decamelize(json_data))

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
