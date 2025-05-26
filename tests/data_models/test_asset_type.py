import pytest
from data_models.trading.asset_type import AssetType


def test_asset_type_enum_values():
    """Test that AssetType enum has expected values."""
    assert AssetType.FxSpot.value == "FxSpot"
    assert AssetType.Stock.value == "Stock"
    assert AssetType.Bond.value == "Bond"
    assert AssetType.Etf.value == "Etf"


def test_asset_type_from_string():
    """Test creating AssetType from string value."""
    assert AssetType("FxSpot") == AssetType.FxSpot
    assert AssetType("Stock") == AssetType.Stock
    assert AssetType("Bond") == AssetType.Bond


def test_asset_type_invalid_value():
    """Test that creating AssetType with invalid value raises ValueError."""
    with pytest.raises(ValueError):
        AssetType("InvalidAssetType")
