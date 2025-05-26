import pytest
from data_models.price.price_type import PriceType


def test_price_type_enum_values():
    """Test that PriceType enum has the expected values."""
    assert PriceType.PIP.value == "pip"
    assert PriceType.PERCENT.value == "percent"
    assert PriceType.PRICE.value == "price"


def test_price_type_string_representation():
    """Test the string representation of PriceType enum values."""
    assert str(PriceType.PIP) == "pip"
    assert str(PriceType.PERCENT) == "percent"
    assert str(PriceType.PRICE) == "price"


def test_price_type_from_string():
    """Test creating PriceType from string value."""
    assert PriceType("pip") == PriceType.PIP
    assert PriceType("percent") == PriceType.PERCENT
    assert PriceType("price") == PriceType.PRICE


def test_price_type_invalid_value():
    """Test that creating PriceType with invalid value raises ValueError."""
    with pytest.raises(ValueError):
        PriceType("invalid_value")


def test_price_type_equality():
    """Test equality comparison of PriceType enum values."""
    assert PriceType.PIP == PriceType.PIP
    assert PriceType.PERCENT == PriceType.PERCENT
    assert PriceType.PRICE == PriceType.PRICE
    assert PriceType.PIP != PriceType.PERCENT
    assert PriceType.PERCENT != PriceType.PRICE
    assert PriceType.PRICE != PriceType.PIP


def test_price_type_identity():
    """Test identity comparison of PriceType enum values."""
    assert PriceType.PIP is PriceType.PIP
    assert PriceType.PERCENT is PriceType.PERCENT
    assert PriceType.PRICE is PriceType.PRICE
    assert PriceType.PIP is not PriceType.PERCENT
    assert PriceType.PERCENT is not PriceType.PRICE
    assert PriceType.PRICE is not PriceType.PIP
