def calculate_tick_size(price: float) -> float:
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
    for threshold, tick_size in tick_size_map.items():
        if price < threshold:
            return tick_size
    return 10  # Default tick size for prices above the highest threshold
