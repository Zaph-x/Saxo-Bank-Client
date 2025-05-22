from data_models.price.price_info import PriceInfo
from data_models.trade_payload import MarketOrderTradePayload, LimitOrderTradePayload
from data_models.price.price_type import PriceType
from utils.number_utils import round_decimal_to_nearest_x

tick_size_map = {
    0.4999: 0.0001,
    0.9995: 0.0005,
    4.999: 0.001,
    9.995: 0.005,
    49.99: 0.01,
    99.95: 0.05,
    499.9: 0.1,
    999.5: 0.5,
    4999.5: 1,
    9999.5: 5,
}


def get_tick_size(price: float) -> float:
    """
    Get the tick size for a given price.

    Args:
        price (float): The price of the asset.

    Returns:
        float: The tick size.
    """
    for threshold, tick_size in tick_size_map.items():
        if price < threshold:
            return tick_size
    return 0.0001


def calculate_pip_price(self, price_info: PriceInfo, pips: int) -> float:
    """
    Calculate the pip price for a given price info and number of pips.

    Args:
        price_info (PriceInfo): The price information of the asset.
        pips (int): The number of pips.

    Returns:
        float: The pip price.
    """
    if price_info.allow_decimal_pips:
        return round_decimal_to_nearest_x(
            price_info.ask,
            price_info.get_decimal_size(),
            pips,
        )
    else:
        return round_decimal_to_nearest_x(
            price_info.ask,
            price_info.get_decimal_size(),
            pips,
        )


def calculate_take_profit(
    price_info: PriceInfo,
    order_payload: MarketOrderTradePayload | LimitOrderTradePayload,
) -> float:
    """
    Calculate the take profit price based on the order payload and price information.

    Args:
        price_info (PriceInfo): The price information of the asset.
        order_payload (MarketOrderTradePayload | LimitOrderTradePayload): The order payload.

    Returns:
        float: The calculated take profit price.
    """

    take_profit = order_payload.sl_tp.take_profit
    if take_profit.price <= 0:
        raise ValueError(f"Take profit price must be above 0: {take_profit.price}")
    if order_payload.side == "long":
        if take_profit.type == PriceType.PIP:
            raise NotImplementedError("PIP calculation is not implemented.")
        elif take_profit.type == PriceType.PRICE:
            take_profit_price = take_profit.price
        elif take_profit.type == PriceType.PERCENT:
            take_profit_price = price_info.ask * (1 + take_profit.price / 100)
        else:
            raise ValueError(f"Invalid take profit type: {take_profit.type}")
    elif order_payload.side == "short":
        if take_profit.type == PriceType.PIP:
            raise NotImplementedError("PIP calculation is not implemented.")
        elif take_profit.type == PriceType.PRICE:
            take_profit_price = take_profit.price
        elif take_profit.type == PriceType.PERCENT:
            take_profit_price = price_info.bid * (1 - take_profit.price / 100)
        else:
            raise ValueError(f"Invalid take profit type: {take_profit.type}")
    else:
        raise ValueError(f"Invalid side: {order_payload.side}")
    if take_profit_price < 0:
        raise ValueError(f"Take profit price cannot be negative: {take_profit_price}")
    return take_profit_price


def calculate_stop_loss(
    price_info: PriceInfo,
    order_payload: MarketOrderTradePayload | LimitOrderTradePayload,
) -> float:
    """
    Calculate the stop loss price based on the order payload and price information.

    Args:
        price_info (PriceInfo): The price information of the asset.
        order_payload (MarketOrderTradePayload | LimitOrderTradePayload): The order payload.

    Returns:
        float: The calculated stop loss price.
    """
    stop_loss = order_payload.sl_tp.stop_loss

    if stop_loss.price <= 0:
        raise ValueError(f"Stop loss price must be above 0: {stop_loss.price}")
    if order_payload.side == "long":
        if stop_loss.type == PriceType.PIP:
            raise NotImplementedError("PIP calculation is not implemented.")
        elif stop_loss.type == PriceType.PRICE:
            stop_loss_price = stop_loss.price
        elif stop_loss.type == PriceType.PERCENT:
            stop_loss_price = price_info.ask * (1 - stop_loss.price / 100)
        else:
            raise ValueError(f"Invalid stop loss type: {stop_loss.type}")
    elif order_payload.side == "short":
        if stop_loss.type == PriceType.PIP:
            raise NotImplementedError("PIP calculation is not implemented.")
        elif stop_loss.type == PriceType.PRICE:
            stop_loss_price = stop_loss.price
        elif stop_loss.type == PriceType.PERCENT:
            stop_loss_price = price_info.bid * (1 + stop_loss.price / 100)
        else:
            raise ValueError(f"Invalid stop loss type: {stop_loss.type}")
    else:
        raise ValueError(f"Invalid side: {order_payload.side}")

    if stop_loss_price < 0:
        raise ValueError(f"Stop loss price cannot be negative: {stop_loss_price}")
    return stop_loss_price
