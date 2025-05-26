import pytest
import json
import jsonschema
from data_models.json_model_base import JsonModelBase


class SimpleJsonModel(JsonModelBase):
    """A simple implementation of JsonModelBase for testing purposes"""
    __schema__ = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "value": {"type": "number", "minimum": 0},
        },
        "required": ["name", "value"],
        "additionalProperties": False,
    }
    
    def __init__(self, name: str, value: float):
        self.name = name
        self.value = value


class NestedJsonModel(JsonModelBase):
    """A nested implementation of JsonModelBase for testing purposes"""
    __schema__ = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "test_model": {"type": "object"},
        },
        "required": ["id", "test_model"],
        "additionalProperties": False,
    }
    
    def __init__(self, id: str, test_model: SimpleJsonModel):
        self.id = id
        self.test_model = test_model


def test_json_model_base_to_json():
    """Test that to_json correctly serializes a model to JSON."""
    model = SimpleJsonModel(name="test", value=10)
    json_str = model.to_json()
    json_dict = json.loads(json_str)
    
    assert json_dict["name"] == "test"
    assert json_dict["value"] == 10


def test_json_model_base_to_json_camelizes_keys():
    """Test that to_json correctly camelizes keys."""
    model = SimpleJsonModel(name="test_name", value=10)
    model.snake_case_key = "value"
    
    json_str = model.to_json()
    json_dict = json.loads(json_str)
    
    assert "snakeCaseKey" in json_dict
    assert json_dict["snakeCaseKey"] == "value"


def test_json_model_base_from_json_with_string():
    """Test that from_json correctly deserializes a JSON string."""
    json_str = """{"name":"test","value":10}"""
    model = SimpleJsonModel.from_json(json_str)
    
    assert model.name == "test"
    assert model.value == 10


def test_json_model_base_from_json_with_dict():
    """Test that from_json correctly deserializes a dict."""
    json_dict = {"name": "test", "value": 10}
    model = SimpleJsonModel.from_json(json_dict)
    
    assert model.name == "test"
    assert model.value == 10



def test_json_model_base_validate_json_with_string():
    """Test that validate_json correctly validates a JSON string."""
    json_str = """{"name":"test","value":10}"""
    SimpleJsonModel.validate_json(json_str)
    # No assertion needed, test passes if no exception is raised


def test_json_model_base_validate_json_with_dict():
    """Test that validate_json correctly validates a dict."""
    json_dict = {"name": "test", "value": 10}
    SimpleJsonModel.validate_json(json_dict)
    # No assertion needed, test passes if no exception is raised


def test_json_model_base_validate_json_with_invalid_json():
    """Test that validate_json raises an exception for invalid JSON."""
    with pytest.raises(jsonschema.exceptions.ValidationError):
        SimpleJsonModel.validate_json({"name": "test", "value": -1})  # value should be >= 0


def test_json_model_base_validate_json_missing_required():
    """Test that validate_json raises an exception when a required field is missing."""
    with pytest.raises(jsonschema.exceptions.ValidationError):
        SimpleJsonModel.validate_json({"name": "test"})  # Missing required 'value' field


def test_json_model_base_validate_json_additional_properties():
    """Test that validate_json raises an exception when there are additional properties."""
    with pytest.raises(jsonschema.exceptions.ValidationError):
        SimpleJsonModel.validate_json({"name": "test", "value": 10, "extra": "field"})


def test_nested_json_model_to_json():
    """Test that to_json correctly serializes a nested model to JSON."""
    inner_model = SimpleJsonModel(name="inner", value=5)
    nested_model = NestedJsonModel(id="outer", test_model=inner_model)
    
    json_str = nested_model.to_json()
    json_dict = json.loads(json_str)
    
    assert json_dict["id"] == "outer"
    assert isinstance(json_dict["testModel"], dict)
    assert json_dict["testModel"]["name"] == "inner"
    assert json_dict["testModel"]["value"] == 5


def test_nested_json_model_from_json():
    """Test that from_json correctly deserializes a nested model."""
    json_dict = {
        "id": "outer",
        "test_model": {
            "name": "inner",
            "value": 5
        }
    }
    
    # This is now supported
    nested_model = NestedJsonModel.from_json(json_dict)
    
    assert nested_model.id == "outer"
    assert isinstance(nested_model.test_model, dict)
    assert nested_model.test_model["name"] == "inner"
    assert nested_model.test_model["value"] == 5
