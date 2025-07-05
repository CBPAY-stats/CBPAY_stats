import requests
import json
import time

# CoinMarketCap API configuration
COINMARKETCAP_API_KEY = "db7ad51a-325c-4047-8799-005c2664b776"
COINMARKETCAP_API_URL = "https://pro-api.coinmarketcap.com/v1"
COINMARKETCAP_CBPAY_ID = "32992" # Corrected ID for CBPAY

# CoinGecko API configuration (will be used as fallback)
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
COINGECKO_COIN_ID = "coinbarpay"

# MEXC API configuration (will be removed if CoinMarketCap works reliably)
MEXC_API_URL = "https://api.mexc.com/api/v3"
MEXC_SYMBOL = "CBPAY_USDT"

# XDB Chain Horizon API configuration
XDB_HORIZON_URL = "https://horizon.livenet.xdbchain.com/"
CBPAY_ASSET_CODE = "CBPAY"
CBPAY_ISSUER_ACCOUNT = "GD7PT6VAXH227WBYR5KN3OYKGSNXVETMYZUP3R62DFX3BBC7GGQ"

def get_cbpay_market_data():
    print("Fetching CoinMarketCap data...")
    try:
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
        }
        params = {
            'id': COINMARKETCAP_CBPAY_ID,
            'convert': 'USD'
        }
        response = requests.get(f"{COINMARKETCAP_API_URL}/cryptocurrency/quotes/latest", headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        
        price_usd = None
        market_cap_usd = None
        volume_24h_usd = None
        change_24h_usd = None

        if data and "data" in data and str(COINMARKETCAP_CBPAY_ID) in data["data"]:
            cbpay_data = data["data"][str(COINMARKETCAP_CBPAY_ID)]
            quote = cbpay_data.get("quote", {}).get("USD", {})
            price_usd = quote.get("price")
            market_cap_usd = quote.get("market_cap")
            volume_24h_usd = quote.get("volume_24h")
            change_24h_usd = quote.get("percent_change_24h")
            
        market_data = {
            "price_usd": price_usd,
            "market_cap_usd": market_cap_usd,
            "volume_24h_usd": volume_24h_usd,
            "change_24h_usd": change_24h_usd,
            "last_updated_at": int(time.time())
        }
        with open("cbpay_market_data.json", "w") as f:
            json.dump(market_data, f, indent=4)
        print("cbpay_market_data.json updated from CoinMarketCap.")
        return market_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CoinMarketCap data: {e}")
        print("Falling back to CoinGecko for market data...")
        return get_cbpay_market_data_coingecko()

def get_cbpay_market_data_coingecko():
    print("Fetching CoinGecko data...")
    try:
        response = requests.get(f"{COINGECKO_API_URL}/simple/price?ids={COINGECKO_COIN_ID}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true")
        response.raise_for_status()
        data = response.json()
        
        price_usd = data.get(COINGECKO_COIN_ID, {}).get("usd")
        market_cap_usd = data.get(COINGECKO_COIN_ID, {}).get("usd_market_cap")
        volume_24h_usd = data.get(COINGECKO_COIN_ID, {}).get("usd_24h_vol")
        change_24h_usd = data.get(COINGECKO_COIN_ID, {}).get("usd_24h_change")
        last_updated_at = data.get(COINGECKO_COIN_ID, {}).get("last_updated_at")

        market_data = {
            "price_usd": price_usd,
            "market_cap_usd": market_cap_usd,
            "volume_24h_usd": volume_24h_usd,
            "change_24h_usd": change_24h_usd,
            "last_updated_at": last_updated_at
        }
        with open("cbpay_market_data.json", "w") as f:
            json.dump(market_data, f, indent=4)
        print("cbpay_market_data.json updated from CoinGecko.")
        return market_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CoinGecko data: {e}")
        return None

def get_cbpay_holders():
    print("Fetching CBPAY holders...")
    holders = []
    cursor = None
    while True:
        try:
            params = {
                "asset": f"{CBPAY_ASSET_CODE}:{CBPAY_ISSUER_ACCOUNT}",
                "limit": 200,
                "order": "asc"
            }
            if cursor:
                params["cursor"] = cursor

            response = requests.get(f"{XDB_HORIZON_URL}accounts", params=params)
            response.raise_for_status()
            data = response.json()
            
            for record in data["_embedded"]["records"]:
                for balance in record["balances"]:
                    if balance.get("asset_code") == CBPAY_ASSET_CODE and balance.get("asset_issuer") == CBPAY_ISSUER_ACCOUNT:
                        holders.append({
                            "address": record["account_id"],
                            "balance": float(balance["balance"])
                        })
            
            if "_links" in data and "next" in data["_links"]:
                next_link = data["_links"]["next"]["href"]
                if "cursor=" in next_link:
                    cursor_part = next_link.split("cursor=")[1]
                    if "&" in cursor_part:
                        cursor = cursor_part.split("&")[0]
                    else:
                        cursor = cursor_part
                else:
                    break
            else:
                break
            time.sleep(0.5) 
        except requests.exceptions.RequestException as e:
            print(f"Error fetching XDB Chain accounts: {e}")
            break
    
    holders.sort(key=lambda x: x["balance"], reverse=True)

    with open("cbpay_holders.json", "w") as f:
        json.dump(holders, f, indent=4)
    print("cbpay_holders.json updated.")
    return holders

def get_cbpay_large_transactions():
    print("Fetching top 10 large transactions (>= 100000 CBPAY)....")
    large_transactions = []
    try:
        response = requests.get(f"{XDB_HORIZON_URL}payments?asset_code={CBPAY_ASSET_CODE}&asset_issuer={CBPAY_ISSUER_ACCOUNT}&limit=10&order=desc")
        response.raise_for_status()
        data = response.json()

        for record in data["_embedded"]["records"]:
            if record["type"] == "payment" and "asset_code" in record and record["asset_code"] == CBPAY_ASSET_CODE:
                amount = float(record["amount"])
                if amount >= 100000:
                    large_transactions.append({
                        "id": record["id"],
                        "from": record["from"],
                        "to": record["to"],
                        "amount": amount,
                        "asset_code": record["asset_code"],
                        "asset_issuer": record["asset_issuer"],
                        "created_at": record["created_at"]
                    })
        
        with open("cbpay_large_transactions.json", "w") as f:
            json.dump(large_transactions, f, indent=4)
        print("cbpay_large_transactions.json updated with 10 transactions.")
        return large_transactions
    except requests.exceptions.RequestException as e:
        print(f"Error fetching large transactions: {e}")
        return None

if __name__ == "__main__":
    market_data = get_cbpay_market_data()
    if market_data:
        print(f"Market Data: {market_data}")
    
    holders_data = get_cbpay_holders()
    if holders_data:
        print(f"Total Holders: {len(holders_data)}")
        print(f"Top 5 Holders:")
        for i, holder in enumerate(holders_data[:5]):
            print(f"  {i+1}. Address: {holder['address']}, Balance: {holder['balance']}")

    large_transactions = get_cbpay_large_transactions()
    if large_transactions:
        print(f"Large Transactions: {len(large_transactions)}")
        for tx in large_transactions:
            print(f"  Amount: {tx['amount']}, From: {tx['from']}, To: {tx['to']}")


