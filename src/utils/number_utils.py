def round_decimal_to_nearest_x(price, x, n_decimals):
    """
    Round a decimal number to the nearest multiple of x.

    Args:
        price (float): The decimal number to round.
        x (int): The multiple to round to.
        n_decimals (int): The number of decimal places to round to.

    Returns:
        float: The rounded number.
    """
    # n_decimals is the number of decimal places to round to
    # This should be a positive integer
    if not isinstance(n_decimals, int) or n_decimals <= 0:
        raise ValueError("n_decimals must be a positive integer")
    if not isinstance(price, float):
        raise ValueError("price must be an integer or float")
    if not isinstance(x, int):
        raise ValueError("x must be an integer")

    n_decimals = "1" + "0" * n_decimals
    n_decimals = int(n_decimals)

    integer_part = int(price)
    decimal_part = price - integer_part
    rounded_decimal = round(decimal_part * n_decimals / x) * x / n_decimals
    result = integer_part + rounded_decimal
    return round(result, x)

def round_decimal_to_nearest_tick(price, tick_size, precision=None):
    """
    Round a decimal number to the nearest tick size.

    Args:
        price (float): The decimal number to round.
        tick_size (int): The tick size to round to provided by saxo bank.
        precision (int, optional): The number of decimal places to round to. Defaults to None.

    Returns:
        float: The rounded number.
    """
    tick_size = .1/tick_size
    rounded_price = round(price / tick_size) * tick_size

    if precision is not None:
        rounded_price = round(rounded_price, precision)
    return rounded_price
