import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("currency-server")


@mcp.tool()
async def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert an amount between currencies using Frankfurter API."""
    if amount <= 0:
        raise ValueError("Amount must be positive")

    from_currency = from_currency.upper().strip()
    to_currency = to_currency.upper().strip()

    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        response = await client.get(
            "https://api.frankfurter.dev/v1/latest",
            params={
                "amount": amount,
                "from": from_currency,
                "to": to_currency,
            },
        )
        response.raise_for_status()
        data = response.json()

    rates = data.get("rates") or {}
    if to_currency not in rates:
        raise ValueError("Currency conversion failed or unsupported currency")

    return {
        "input": {"amount": amount, "from": from_currency, "to": to_currency},
        "converted_amount": rates[to_currency],
        "date": data.get("date"),
        "provider": "Frankfurter",
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
