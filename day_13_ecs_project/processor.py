import time
import urllib.request
import json

def fetch_exchange_rates():
    print("Starting Financial ETL Pipeline...")
    
    # 1. Reach out to the public internet (This tests our NAT Gateway later!)
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    print(f"Fetching live data from {url}...")
    
    try:
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode('utf-8'))
        
        # 2. Process the data
        usd_to_ngn = data['rates'].get('NGN', 'N/A')
        print(f"SUCCESS: 1 USD = {usd_to_ngn} NGN")
        
        # In a real pipeline, you would use boto3 here to write this to DynamoDB or S3
        print("ETL Job Complete. Shutting down securely.")
        
    except Exception as e:
        print(f"CRITICAL ERROR: Could not reach the internet. {e}")
        # If the NAT Gateway fails, this script will crash here.

if __name__ == "__main__":
    fetch_exchange_rates()