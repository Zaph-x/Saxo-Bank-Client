from data_models.saxo.place_related_or_oco_order import PlaceRelatedOrOcoOrderModel


def test_can_deserialise_related_or_oco_oder_without_order_duration():
    data_dict = {
        "AccountKey": "LZTc7DdejXODf-WSl2aCyQ==",
        "Amount": 100000,
        "AssetType": "FxSpot",
        "BuySell": "Sell",
        "OrderPrice": 1.13,
        "OrderType": "Limit",
        "Uic": 21,
    }

    order = PlaceRelatedOrOcoOrderModel(**data_dict)

    assert order.AccountKey == "LZTc7DdejXODf-WSl2aCyQ=="
    assert order.Amount == 100000
    assert order.AssetType == "FxSpot"
    assert order.BuySell == "Sell"
