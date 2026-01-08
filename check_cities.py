import requests
import json

url = "https://dev-sitex-1858428749.wix-development-sites.org/_functions/mlsrawdata?page=1&limit=1000"
response = requests.get(url, timeout=30)

if response.status_code == 200:
    data = response.json()
    items = data.get("items", [])
    
    # Get all unique cities
    cities = {}
    for item in items:
        city = item.get("city", "Unknown")
        cities[city] = cities.get(city, 0) + 1
    
    print("🏙️  Available Cities in MLS Data:\n")
    for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True):
        print(f"   {city}: {count} properties")
    
    print(f"\n✅ Total: {len(items)} properties across {len(cities)} cities")
else:
    print(f"❌ Error: {response.status_code}")
