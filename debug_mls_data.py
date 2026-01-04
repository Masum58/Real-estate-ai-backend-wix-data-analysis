import requests
import json
# Fetch MLS data
url = "https://dev-sitex-1858428749.wix-development-sites.org/_functions/mlsrawdata"
response = requests.get(url, timeout=30)

if response.status_code == 200:
    data = response.json()
    items = data.get("items", [])
    
    print(f"✅ Total items: {len(items)}")
    
    if items:
        print("\n📊 First item keys:")
        print(json.dumps(list(items[0].keys()), indent=2))
        
        print("\n🏠 First item sample:")
        print(json.dumps(items[0], indent=2)[:500])
        
        # Check for city-related fields
        print("\n🔍 Looking for location fields:")
        first_item = items[0]
        for key in first_item.keys():
            if any(word in key.lower() for word in ['city', 'town', 'location', 'address', 'zip', 'postal']):
                print(f"  - {key}: {first_item[key]}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
