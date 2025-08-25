from data_models.price.price_info import PriceInfo
from data_models.trade_payload import MarketOrderTradePayload, LimitOrderTradePayload
from data_models.price.price_type import PriceType
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

def get_tick_size(price: float, tick_schema: list[dict[str,float]]) -> Tuple[float, float]:
    """
    Get the tick size for a given price.

    Args:
        price (float): The price of the asset.

    Returns:
        float: The tick size.
    """
    i = 0
    while i < len(tick_schema) and price >= tick_schema[i]["HighPrice"]:
        i += 1

    tick_size = tick_schema[i]['TickSize'] if i < len(tick_schema) else tick_schema[-1]['TickSize']
    high_price = tick_schema[i]['price'] if i < len(tick_schema) else tick_schema[-1]['price']
    if tick_size <= 0:
        raise ValueError(f"Tick size must be above 0: {tick_size}")
    return high_price, tick_size



def calculate_pip_price(current_price: float, pips: int, tick_schema: list[dict[str,float]]) -> float:
    """
    Calculate the pip price for a given price info and number of pips.

    Args:
        price_info (PriceInfo): The price information of the asset.
        pips (int): The number of pips.

    Returns:
        float: The pip price.
    """
    if not tick_schema:
        raise ValueError("Tick schema cannot be empty.")
    
    high_price, initial_tick_size = get_tick_size(current_price, tick_schema)
    
    # check if pips exceed the max price defined in the tick schema
    initial_pricing = current_price + pips * initial_tick_size
    if initial_pricing <= high_price:
        return initial_pricing

    logger.debug(f"Current price {current_price} with pips {pips} exceeds high price {high_price}. Adjusting to high price.")
    pip_distance_to_high = high_price - current_price / initial_tick_size
    if pip_distance_to_high < 0:
        raise ValueError(f"Pip distance to high price cannot be negative: {pip_distance_to_high}")

    adjusted_pips = pip_distance_to_high // initial_tick_size
    if adjusted_pips < 0:
        raise ValueError(f"Adjusted pips cannot be negative: {adjusted_pips}")

    return 0

def calculate_take_profit(
    price_info: PriceInfo,
    order_payload: MarketOrderTradePayload | LimitOrderTradePayload,
    tick_size: float
) -> float:
    """
    Calculate the take profit price based on the order payload and price information.

    Args:
        price_info (PriceInfo): The price information of the asset.
        order_payload (MarketOrderTradePayload | LimitOrderTradePayload): The order payload.
        increment (float): The increment value to adjust the take profit price.

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
            take_profit_price = round_to_nearest_tick_decimal(take_profit.price, tick_size)
        elif take_profit.type == PriceType.PERCENT:
            take_profit_price = round_to_nearest_tick_decimal(price_info.ask * (1 + take_profit.price / 100), tick_size)
        else:
            raise ValueError(f"Invalid take profit type: {take_profit.type}")
    elif order_payload.side == "short":
        if take_profit.type == PriceType.PIP:
            raise NotImplementedError("PIP calculation is not implemented.")
        elif take_profit.type == PriceType.PRICE:
            take_profit_price = round_to_nearest_tick_decimal(take_profit.price, tick_size)
        elif take_profit.type == PriceType.PERCENT:
            take_profit_price = round_to_nearest_tick_decimal(price_info.bid * (1 - take_profit.price / 100), tick_size)
        else:
            raise ValueError(f"Invalid take profit type: {take_profit.type}")
    else:
        raise ValueError(f"Invalid side: {order_payload.side}")
    if take_profit_price < 0:
        raise ValueError(f"Take profit price cannot be negative: {take_profit_price}")
    return take_profit_price

def round_to_nearest_tick_decimal(price: float, tick_size: float) -> float:
    """
    Rounds a price to the nearest decimal that aligns with the given tick size.
    """
    ticks = round(price / tick_size)
    rounded_price = ticks * tick_size
    return round(rounded_price, 10)


def calculate_stop_loss(
    price_info: PriceInfo,
    order_payload: MarketOrderTradePayload | LimitOrderTradePayload,
    tick_size: float
) -> float:
    """
    Calculate the stop loss price based on the order payload and price information.

    Args:
        price_info (PriceInfo): The price information of the asset.
        order_payload (MarketOrderTradePayload | LimitOrderTradePayload): The order payload.
        increment (float): The increment value to adjust the stop loss price.

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
            stop_loss_price = round_to_nearest_tick_decimal(stop_loss.price, tick_size)
        elif stop_loss.type == PriceType.PERCENT:
            stop_loss_price = round_to_nearest_tick_decimal(price_info.ask * (1 - stop_loss.price / 100), tick_size)
        else:
            raise ValueError(f"Invalid stop loss type: {stop_loss.type}")
    elif order_payload.side == "short":
        if stop_loss.type == PriceType.PIP:
            raise NotImplementedError("PIP calculation is not implemented.")
        elif stop_loss.type == PriceType.PRICE:
            stop_loss_price = round_to_nearest_tick_decimal(stop_loss.price, tick_size)
        elif stop_loss.type == PriceType.PERCENT:
            stop_loss_price = round_to_nearest_tick_decimal(price_info.bid * (1 + stop_loss.price / 100), tick_size)
        else:
            raise ValueError(f"Invalid stop loss type: {stop_loss.type}")
    else:
        raise ValueError(f"Invalid side: {order_payload.side}")

    if stop_loss_price < 0:
        raise ValueError(f"Stop loss price cannot be negative: {stop_loss_price}")
    return stop_loss_price
