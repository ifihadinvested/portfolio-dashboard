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
    
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.text}")
    
    # Parse reference code
    root = ET.fromstring(response.content)
    
    status = root.find('Status')
    if status is None or status.text != 'Success':
        error_msg = root.find('ErrorMessage')
        error_text = error_msg.text if error_msg is not None else root.text
        raise Exception(f"IBKR request failed: {error_text}")
    
    reference_code = root.find('ReferenceCode').text
    print(f"✅ Reference code: {reference_code}")
    
    # Step 2: Poll until report ready (max 60 seconds)
    retrieve_url = "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement"
    
    for attempt in range(12):  # Try 12 times (60 seconds total)
        print(f"Attempt {attempt + 1}/12: Waiting 5 seconds...")
        time.sleep(5)
        
        params = {
            't': IBKR_TOKEN,
            'q': reference_code,
            'v': '3'
        }
        
        response = requests.get(retrieve_url, params=params)
        
        if response.status_code != 200:
            print(f"Status {response.status_code}, retrying...")
            continue
        
        # Check if it's FlexQueryResponse (data) or FlexStatementResponse (still processing)
        if response.text.strip().startswith('<?xml'):
            try:
                test_root = ET.fromstring(response.content)
                
                # Check if it's the actual data (FlexQueryResponse) or status message
                if test_root.tag == 'FlexQueryResponse':
                    print(f"✅ Portfolio data received! ({len(response.text)} bytes)")
                    
                    # Save XML
                    with open('portfolio_data.xml', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    return response.text
                elif test_root.tag == 'FlexStatementResponse':
                    status_elem = test_root.find('Status')
                    if status_elem is not None:
                        print(f"Status: {status_elem.text} - still processing...")
                else:
                    print(f"Unexpected root tag: {test_root.tag}")
            except ET.ParseError:
                print(f"Response not valid XML yet, retrying...")
                continue
    
    raise Exception("Timeout: IBKR report not ready after 60 seconds")

if __name__ == "__main__":
    fetch_flex_report()
