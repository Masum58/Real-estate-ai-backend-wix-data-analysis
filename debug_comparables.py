import requests
from app.models.subject_property import SubjectProperty
from app.services.comparable_selector import ComparableSelector

# Fetch all data
print("Fetching 46,500 properties...")
response = requests.get("https://fire-ai-mls-raw-data.vercel.app/mls-data", timeout=120)
data = response.json()
items = data.get("items", []) if isinstance(data, dict) else data
print(f"✅ Loaded {len(items)} properties\n")

# Create subject property (510 Martha)
subject = SubjectProperty(
    address="510 Martha Ave",
    city="Charlotte",
    state="NC",
    zip_code="28202",
    bedrooms=3,
    bathrooms=2,
    square_footage=1169,
    year_built=1981,
    condition_score=5,
    user_notes="Debug test",
    email="test@test.com"
)

# Select comparables
selector = ComparableSelector(subject)
comparables = selector.select(items, limit=25)

print(f"Found {len(comparables)} comparables\n")
print("=" * 80)
print("Top 10 Comparables:")
print("=" * 80)

for i, comp in enumerate(comparables[:10], 1):
    distance = comp.get('_distance', 999)
    weight = comp.get('_weight', 1)
    price = comp.get('price', 0)
    sqft = comp.get('areaSqft', 0)
    price_per_sqft = price / sqft if sqft > 0 else 0
    
    print(f"\n{i}. {comp.get('address', 'N/A')}")
    print(f"   City: {comp.get('city', 'N/A')}, {comp.get('state', 'N/A')}")
    print(f"   Price: ${price:,} | Sqft: {sqft:,} | $/Sqft: ${price_per_sqft:.2f}")
    print(f"   Distance: {distance:.2f} mi | Weight: {weight}")
    print(f"   Beds/Baths: {comp.get('bedrooms', 0)}/{comp.get('bathrooms', 0)}")
    print(f"   Year: {comp.get('yearBuilt', 'N/A')}")

# Check for client's specific properties
print("\n" + "=" * 80)
print("Checking for Client's Manual CMA Properties:")
print("=" * 80)

target_addresses = [
    "604 Davis Park",
    "508 Queens",
    "422 Becky",
    "3101 Harvell",
    "3030 Randy",
    "3316 Queens"
]

for target in target_addresses:
    found = [c for c in comparables if target.lower() in c.get('address', '').lower()]
    if found:
        comp = found[0]
        print(f"✅ {target}: ${comp.get('price', 0):,} ({comp.get('_distance', 999):.2f} mi)")
    else:
        # Check if it's in the dataset but not selected
        in_dataset = [p for p in items if target.lower() in p.get('address', '').lower()]
        if in_dataset:
            prop = in_dataset[0]
            print(f"⚠️  {target}: In dataset but NOT selected")
            print(f"    Price: ${prop.get('price', 0):,}")
            print(f"    City: {prop.get('city')}")
            print(f"    Status: {prop.get('status')}")
            print(f"    Beds/Baths: {prop.get('bedrooms')}/{prop.get('bathrooms')}")
            print(f"    Sqft: {prop.get('areaSqft')}")
            print(f"    Year: {prop.get('yearBuilt')}")
        else:
            print(f"❌ {target}: NOT in dataset")

# Calculate average price
if comparables:
    avg_price = sum(c.get('price', 0) for c in comparables) / len(comparables)
    prices = [c.get('price', 0) for c in comparables]
    avg_sqft_list = [c.get('price', 0) / c.get('areaSqft', 1) for c in comparables if c.get('areaSqft', 0) > 0]
    avg_sqft = sum(avg_sqft_list) / len(avg_sqft_list) if avg_sqft_list else 0
    
    print(f"\n" + "=" * 80)
    print(f"Summary:")
    print(f"Average Price: ${avg_price:,.0f}")
    print(f"Min Price: ${min(prices):,}")
    print(f"Max Price: ${max(prices):,}")
    print(f"Average $/Sqft: ${avg_sqft:.2f}")
    print("=" * 80)
