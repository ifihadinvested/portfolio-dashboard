import os
import requests
import time
import xml.etree.ElementTree as ET

IBKR_TOKEN = os.environ['IBKR_TOKEN']
QUERY_ID = os.environ['IBKR_QUERY_ID']

def fetch_flex_report():
    """Fetch IBKR Flex Query report"""
    
    # Step 1: Request report
    request_url = f"https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest"
    params = {
        't': IBKR_TOKEN,
        'q': QUERY_ID,
        'v': '3'
    }
    
    print("Requesting IBKR Flex Report...")
    response = requests.get(request_url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.text}")
    
    # Parse reference code
    root = ET.fromstring(response.content)
    
    if root.find('Status').text != 'Success':
        raise Exception(f"IBKR request failed: {root.find('ErrorMessage').text}")
    
    reference_code = root.find('ReferenceCode').text
    print(f"Reference code: {reference_code}")
    
    # Step 2: Wait and retrieve report
    time.sleep(5)  # IBKR needs time to generate
    
    retrieve_url = f"https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement"
    params = {
        't': IBKR_TOKEN,
        'q': reference_code,
        'v': '3'
    }
    
    print("Retrieving report...")
    response = requests.get(retrieve_url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Retrieval failed: {response.text}")
    
    # Save XML
    with open('portfolio_data.xml', 'w') as f:
        f.write(response.text)
    
    print("✅ Portfolio data saved!")
    return response.text

if __name__ == "__main__":
    fetch_flex_report()
