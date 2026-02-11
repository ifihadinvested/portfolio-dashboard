import os
import requests
import time
import xml.etree.ElementTree as ET

IBKR_TOKEN = os.environ['IBKR_TOKEN']
QUERY_ID = os.environ['IBKR_QUERY_ID']

def fetch_flex_report():
    """Fetch IBKR Flex Query report"""
    
    # Step 1: Request report
    request_url = "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest"
    params = {
        't': IBKR_TOKEN,
        'q': QUERY_ID,
        'v': '3'
    }
    
    print(f"Requesting IBKR Flex Report (Query ID: {QUERY_ID})...")
    response = requests.get(request_url, params=params)
    
    print(f"Request status: {response.status_code}")
    print(f"Response: {response.text[:500]}")  # Print first 500 chars
    
    if response.status_code != 200:
        raise Exception(f"Request failed with status {response.status_code}: {response.text}")
    
    # Parse reference code
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"ERROR parsing request response: {e}")
        print(f"Full response: {response.text}")
        raise
    
    status = root.find('Status')
    if status is None or status.text != 'Success':
        error_msg = root.find('ErrorMessage')
        error_text = error_msg.text if error_msg is not None else 'Unknown error'
        raise Exception(f"IBKR request failed: {error_text}")
    
    reference_code = root.find('ReferenceCode').text
    print(f"✅ Reference code: {reference_code}")
    
    # Step 2: Wait and retrieve report
    print("Waiting 10 seconds for IBKR to generate report...")
    time.sleep(10)  # Increase wait time
    
    retrieve_url = "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement"
    params = {
        't': IBKR_TOKEN,
        'q': reference_code,
        'v': '3'
    }
    
    print("Retrieving report...")
    response = requests.get(retrieve_url, params=params)
    
    print(f"Retrieval status: {response.status_code}")
    print(f"Response first 500 chars: {response.text[:500]}")
    
    if response.status_code != 200:
        raise Exception(f"Retrieval failed with status {response.status_code}: {response.text}")
    
    # Check if response is valid XML
    if not response.text.strip().startswith('<?xml'):
        print(f"ERROR: Response is not XML!")
        print(f"Full response: {response.text}")
        raise Exception("IBKR did not return XML data")
    
    # Save XML
    with open('portfolio_data.xml', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print(f"✅ Portfolio data saved! ({len(response.text)} bytes)")
    return response.text

if __name__ == "__main__":
    fetch_flex_report()
