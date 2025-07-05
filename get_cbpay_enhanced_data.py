
import requests
import json
import os
import time

# CoinMarketCap API Key (replace with your actual key)
CMC_API_KEY = "db7ad51a-325c-4047-8799-005c2664b776"

# CoinGecko API URL for coin list
COINGECKO_COINS_LIST_URL = "https://api.coingecko.com/api/v3/coins/list"

# CoinMarketCap API URL for quotes latest
CMC_QUOTES_LATEST_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

# XDB Chain Horizon API URL for accounts (holders)
XDB_HORIZON_URL = "https://horizon.livenet.xdbchain.com/accounts"

# CBPAY Asset details
CBPAY_ASSET_CODE = "CBPAY"
CBPAY_ASSET_ISSUER = "GD7PT6VAXH227WBYR5KN3OYKGSNXVETMYZUP3R62DFX3BBC7GGQ"

# File paths
COINGECKO_COINS_LIST_FILE = "coingecko_coins_list.json"
COINMARKETCAP_ID_MAP_FILE = "coinmarketcap_id_map.json"
CBPAY_MARKET_DATA_FILE = "cbpay_market_data.json"
CBPAY_HOLDERS_FILE = "cbpay_holders.json"
CBPAY_LARGE_TRANSACTIONS_FILE = "cbpay_large_transactions.json"

def get_coingecko_coins_list():
    """Fetches the list of coins from CoinGecko and saves it to a JSON file."""
    try:
        response = requests.get(COINGECKO_COINS_LIST_URL)
        response.raise_for_status()
        coins_list = response.json()
        with open(COINGECKO_COINS_LIST_FILE, "w") as f:
            json.dump(coins_list, f, indent=4)
        print(f"Successfully fetched and saved CoinGecko coins list to {COINGECKO_COINS_LIST_FILE}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CoinGecko coins list: {e}")

def get_coinmarketcap_id_map():
    """Fetches the CoinMarketCap ID map for CBPAY and saves it to a JSON file."""
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": CMC_API_KEY,
    }
    params = {
        "symbol": CBPAY_ASSET_CODE,
    }
    try:
        response = requests.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/map", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        with open(COINMARKETCAP_ID_MAP_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Successfully fetched and saved CoinMarketCap ID map to {COINMARKETCAP_ID_MAP_FILE}")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CoinMarketCap ID map: {e}")
        return None

def get_cbpay_market_data():
    """Fetches CBPAY market data from CoinMarketCap and saves it to a JSON file."""
    # First, try to load the CoinMarketCap ID map
    cmc_id = None
    if os.path.exists(COINMARKETCAP_ID_MAP_FILE):
        with open(COINMARKETCAP_ID_MAP_FILE, "r") as f:
            cmc_map = json.load(f)
            if cmc_map and "data" in cmc_map and len(cmc_map["data"]) > 0:
                cmc_id = cmc_map["data"][0]["id"]
    
    # If ID map not found or empty, try to fetch it
    if not cmc_id:
        cmc_map = get_coinmarketcap_id_map()
        if cmc_map and "data" in cmc_map and len(cmc_map["data"]) > 0:
            cmc_id = cmc_map["data"][0]["id"]

    if not cmc_id:
        print("Could not retrieve CoinMarketCap ID for CBPAY. Cannot fetch market data.")
        return

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": CMC_API_KEY,
    }
    params = {
        "id": cmc_id,
        "convert": "USD"
    }
    try:
        response = requests.get(CMC_QUOTES_LATEST_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        cbpay_data = data["data"][str(cmc_id)]
        price = cbpay_data["quote"]["USD"]["price"]
        market_cap = cbpay_data["quote"]["USD"]["market_cap"]
        volume_24h = cbpay_data["quote"]["USD"]["volume_24h"]
        percent_change_24h = cbpay_data["quote"]["USD"]["percent_change_24h"]

        market_data = {
            "price_usd": price,
            "market_cap_usd": market_cap,
            "volume_24h_usd": volume_24h,
            "percent_change_24h": percent_change_24h,
            "last_updated": time.time()
        }

        with open(CBPAY_MARKET_DATA_FILE, "w") as f:
            json.dump(market_data, f, indent=4)
        print(f"Successfully fetched and saved CBPAY market data to {CBPAY_MARKET_DATA_FILE}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CBPAY market data from CoinMarketCap: {e}")
    except KeyError as e:
        print(f"Error parsing CoinMarketCap data: Missing key {e}. Response: {data}")

def get_cbpay_holders():
    """Fetches CBPAY holders from XDB Chain Horizon and saves to a JSON file."""
    params = {
        "asset_code": CBPAY_ASSET_CODE,
        "asset_issuer": CBPAY_ASSET_ISSUER,
        "limit": 200,  # Max limit per request
        "order": "desc"
    }
    try:
        response = requests.get(XDB_HORIZON_URL, params=params)
        response.raise_for_status()
        data = response.json()
        with open(CBPAY_HOLDERS_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Successfully fetched and saved CBPAY holders to {CBPAY_HOLDERS_FILE}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CBPAY holders from XDB Chain Horizon: {e}")

def get_cbpay_large_transactions():
    """Placeholder for fetching large CBPAY transactions."""
    # This function would require a more advanced API or parsing of transaction history.
    # For now, it will create an empty JSON file.
    with open(CBPAY_LARGE_TRANSACTIONS_FILE, "w") as f:
        json.dump([], f, indent=4)
    print(f"Created placeholder for large CBPAY transactions at {CBPAY_LARGE_TRANSACTIONS_FILE}")

if __name__ == "__main__":
    # Ensure the necessary files exist or are fetched
    if not os.path.exists(COINGECKO_COINS_LIST_FILE):
        get_coingecko_coins_list()
    
    if not os.path.exists(COINMARKETCAP_ID_MAP_FILE):
        get_coinmarketcap_id_map()

    get_cbpay_market_data()
    get_cbpay_holders()
    get_cbpay_large_transactions()



