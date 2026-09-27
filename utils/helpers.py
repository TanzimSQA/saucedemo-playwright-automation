import re
from typing import Union


def parse_price(price_str: Union[str, float, int]) -> float:
    """
    Extracts float value from price string like '$29.99' or 'Item total: $29.99'
    """
    if isinstance(price_str, (float, int)):
        return float(price_str)
    
    match = re.search(r"\d+(\.\d+)?", price_str)
    if match:
        return float(match.group(0))
    raise ValueError(f"Could not parse price from string: {price_str}")


def calculate_tax(item_total: float, tax_rate: float = 0.08) -> float:
    """
    Calculates expected tax rounded to 2 decimal places.
    SauceDemo standard tax rate is approximately 8% (0.08).
    """
    return round(item_total * tax_rate, 2)
