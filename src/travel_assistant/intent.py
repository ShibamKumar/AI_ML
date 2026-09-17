import re


def has_weather_signal(query: str) -> bool:
    text = query.lower()
    return any(keyword in text for keyword in ["weather", "forecast", "rain", "temperature"])


def has_currency_signal(query: str) -> bool:
    text = query.lower()
    return any(
        keyword in text
        for keyword in ["convert", "currency", "budget", "sgd", "usd", "inr", "eur", "exchange rate"]
    )


def has_itinerary_signal(query: str) -> bool:
    text = query.lower()
    return any(
        keyword in text
        for keyword in ["itinerary", "plan", "trip", "attraction", "neighbourhood", "neighborhood", "transport"]
    )


def classify_intent(query: str) -> str:
    has_weather = has_weather_signal(query)
    has_currency = has_currency_signal(query)
    has_itinerary = has_itinerary_signal(query)

    if (has_weather or has_currency) and has_itinerary:
        return "combined"
    if has_weather:
        return "weather"
    if has_currency:
        return "currency"
    if has_itinerary:
        return "destination"
    return "destination"


def extract_days(query: str, default_days: int = 3) -> int:
    match = re.search(r"(\d+)\s*day", query.lower())
    if not match:
        return default_days
    days = int(match.group(1))
    return max(1, min(days, 7))


def extract_currency_request(query: str) -> tuple[float, str, str] | None:
    text = query.upper()

    patterns = [
        r"([A-Z]{3})\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:TO|INTO|->)\s*([A-Z]{3})",
        r"([0-9][0-9,]*(?:\.[0-9]+)?)\s*([A-Z]{3})\s*(?:TO|INTO|IN)\s*([A-Z]{3})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            g1, g2, g3 = match.groups()
            if g1.isalpha():
                from_currency, amount_str, to_currency = g1, g2, g3
            else:
                amount_str, from_currency, to_currency = g1, g2, g3
            amount = float(amount_str.replace(",", ""))
            return amount, from_currency, to_currency

    amount_match = re.search(r"([0-9][0-9,]*(?:\.[0-9]+)?)", text)
    currencies = re.findall(r"\b[A-Z]{3}\b", text)
    if amount_match and len(currencies) >= 2:
        amount = float(amount_match.group(1).replace(",", ""))
        return amount, currencies[0], currencies[1]

    return None
