import requests
import json
import datetime
import time

# CoinGecko API configuration
COINGECKO_API_KEY = "CG-8CoKVLYmm4crygn9DeHvFUAk" # Replace with your actual API key
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
COINGECKO_HEADERS = {"x-cg-pro-api-key": COINGECKO_API_KEY}

# XDB Chain Horizon API configuration
HORIZON_URL = "https://horizon.livenet.xdbchain.com"
ASSET_CODE = "CBPAY"
ASSET_ISSUER = "GD7PT6VAXH227WBYR5KN3OYKGSNXVETMYZUP3R62DFX3BBC7GGOBDFJ2"

# --- Function to get CoinGecko data ---
def get_coingecko_data():
    print("Fetching CoinGecko data...")
    try:
        # Get coin ID for CBPAY
        search_url = f"{COINGECKO_API_URL}/search?query=cbpay"
        search_response = requests.get(search_url, headers=COINGECKO_HEADERS)
        search_response.raise_for_status()
        search_data = search_response.json()
        
        cbpay_id = None
        for coin in search_data.get("coins", []):
            if coin["symbol"].upper() == ASSET_CODE and "coinbarpay" in coin["id"].lower():
                cbpay_id = coin["id"]
                break
        
        if not cbpay_id:
            print(f"Could not find CoinGecko ID for {ASSET_CODE}")
            return None

        # Get market data
        market_data_url = f"{COINGECKO_API_URL}/simple/price?ids={cbpay_id}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true"
        market_data_response = requests.get(market_data_url, headers=COINGECKO_HEADERS)
        market_data_response.raise_for_status()
        market_data = market_data_response.json()

        if cbpay_id in market_data:
            data = market_data[cbpay_id]
            return {
                "price_usd": data.get("usd"),
                "market_cap_usd": data.get("usd_market_cap"),
                "volume_24h_usd": data.get("usd_24h_vol"),
                "price_change_24h": data.get("usd_24h_change"),
                "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "source": "CoinGecko"
            }
        else:
            print(f"No market data found for {cbpay_id}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CoinGecko data: {e}")
        return None

# --- Function to get all holders ---
def get_all_holders():
    print("Fetching all CBPAY holders...")
    holders = []
    params = {
        "asset_code": ASSET_CODE,
        "asset_issuer": ASSET_ISSUER,
        "limit": 200, # Max limit per request
        "order": "desc"
    }
    url = f"{HORIZON_URL}/accounts"

    while True:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            records = data.get("_embedded", {}).get("records", [])

            if not records:
                break

            for record in records:
                for balance_entry in record.get("balances", []):
                    if balance_entry.get("asset_code") == ASSET_CODE and balance_entry.get("asset_issuer") == ASSET_ISSUER:
                        holders.append({
                            "address": record["account_id"],
                            "balance": float(balance_entry["balance"])
                        })
                        break # Move to next account after finding CBPAY balance
            
            # Check for next page
            next_link = data.get("_links", {}).get("next", {}).get("href")
            if next_link:
                url = next_link
                params = {} # Reset params as next_link contains all necessary query string
            else:
                break
            time.sleep(0.1) # Be kind to the API

        except requests.exceptions.RequestException as e:
            print(f"Error fetching holders: {e}")
            break
    
    # Sort holders by balance in descending order
    holders.sort(key=lambda x: x["balance"], reverse=True)
    return holders

# --- Function to get large transactions ---
def get_large_transactions(limit=10, threshold=100000):
    print(f"Fetching top {limit} large transactions (>= {threshold} CBPAY)...")
    transactions = []
    params = {
        "asset_code": ASSET_CODE,
        "asset_issuer": ASSET_ISSUER,
        "limit": 200, # Max limit per request
        "order": "desc",
        "cursor": "now"
    }
    url = f"{HORIZON_URL}/payments"

    while len(transactions) < limit:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            records = data.get("_embedded", {}).get("records", [])

            if not records:
                break

            for record in records:
                if record["type"] == "payment" and \
                   record.get("asset_code") == ASSET_CODE and \
                   record.get("asset_issuer") == ASSET_ISSUER and \
                   float(record.get("amount", 0)) >= threshold:
                    transactions.append({
                        "amount": float(record["amount"]),
                        "from": record["from"],
                        "to": record["to"],
                        "date": record["created_at"],
                        "transaction_hash": record["transaction_hash"]
                    })
                    if len(transactions) >= limit:
                        break
            
            # Check for next page
            next_link = data.get("_links", {}).get("next", {}).get("href")
            if next_link:
                url = next_link
                params = {} # Reset params as next_link contains all necessary query string
            else:
                break
            time.sleep(0.1) # Be kind to the API

        except requests.exceptions.RequestException as e:
            print(f"Error fetching large transactions: {e}")
            break
    
    return transactions[:limit]

# --- Main execution ---
if __name__ == "__main__":
    # Get market data
    market_data = get_coingecko_data()
    if market_data:
        with open("cbpay_market_data.json", "w") as f:
            json.dump(market_data, f, indent=4)
        print("cbpay_market_data.json updated.")
    else:
        print("Failed to get market data.")

    # Get all holders
    all_holders = get_all_holders()
    if all_holders:
        with open("cbpay_holders.json", "w") as f:
            json.dump(all_holders, f, indent=4)
        print(f"cbpay_holders.json updated with {len(all_holders)} holders.")
    else:
        print("Failed to get holders data.")

    # Get large transactions
    large_transactions = get_large_transactions(limit=10, threshold=100000) # Get top 10 transactions >= 100,000 CBPAY
    if large_transactions:
        with open("cbpay_large_transactions.json", "w") as f:
            json.dump(large_transactions, f, indent=4)
        print(f"cbpay_large_transactions.json updated with {len(large_transactions)} transactions.")
    else:
        print("Failed to get large transactions.")

    print("Data collection complete.")


