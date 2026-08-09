import urllib.request
import json

def get_crypto_price(coin: str = "bitcoin") -> str:
    """Fetches live cryptocurrency prices in USD, EUR, and INR."""
    coin_id = coin.lower().strip()
    # Common mappings
    mapping = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "sol": "solana",
        "doge": "dogecoin",
        "ada": "cardano",
        "xrp": "ripple"
    }
    coin_id = mapping.get(coin_id, coin_id)

    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,eur,inr"
        req = urllib.request.Request(url, headers={"User-Agent": "Vani/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if coin_id in data:
                prices = data[coin_id]
                return (
                    f"Cryptocurrency: {coin_id.upper()}\n"
                    f"- USD: ${prices.get('usd', 0):,.2f}\n"
                    f"- EUR: EUR {prices.get('eur', 0):,.2f}\n"
                    f"- INR: INR {prices.get('inr', 0):,.2f}"
                )
            else:
                return f"Cryptocurrency '{coin}' not found on CoinGecko."
    except Exception as e:
        return f"Error fetching crypto prices: {e}"

def convert_currency(amount: float, from_curr: str = "USD", to_curr: str = "EUR") -> str:
    """Converts fiat currency amounts using real-time exchange rates."""
    from_code = from_curr.upper().strip()
    to_code = to_curr.upper().strip()

    try:
        url = f"https://open.er-api.com/v6/latest/{from_code}"
        req = urllib.request.Request(url, headers={"User-Agent": "Vani/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("result") == "success":
                rates = data.get("rates", {})
                if to_code in rates:
                    rate = rates[to_code]
                    converted = amount * rate
                    return f"{amount:,.2f} {from_code} = {converted:,.2f} {to_code} (Rate: 1 {from_code} = {rate:.4f} {to_code})"
                else:
                    return f"Currency code '{to_code}' not supported."
    except Exception as e:
        return f"Error converting currency: {e}"
    return "Currency conversion failed."

def get_stock_price(symbol: str = "AAPL") -> str:
    """Fetches quote summary for stock tickers."""
    ticker = symbol.upper().strip()
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            result = data.get("chart", {}).get("result", [])
            if result:
                meta = result[0].get("meta", {})
                price = meta.get("regularMarketPrice")
                currency = meta.get("currency", "USD")
                prev_close = meta.get("chartPreviousClose")
                change = price - prev_close if price and prev_close else 0.0
                pct = (change / prev_close * 100.0) if prev_close else 0.0
                sign = "+" if change >= 0 else ""

                return (
                    f"Stock Ticker: {ticker}\n"
                    f"• Current Price: {price:.2f} {currency}\n"
                    f"• Previous Close: {prev_close:.2f} {currency}\n"
                    f"• Day Change: {sign}{change:.2f} ({sign}{pct:.2f}%)"
                )
    except Exception as e:
        return f"Error fetching stock ticker '{ticker}': {e}"
    return f"Stock information for '{ticker}' unavailable."
