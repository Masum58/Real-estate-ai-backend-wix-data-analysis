from typing import Dict, List


# 🔥 UPDATED: Mapping to match actual MLS Grid API field names
FIELD_MAPPING = {
    # Property details
    "BedroomsTotal": "bedrooms",
    "BathroomsFull": "bathrooms_full",
    "BathroomsHalf": "bathrooms_half",
    "LivingArea": "areaSqft",
    "BuildingAreaTotal": "buildingAreaTotal",
    "ClosePrice": "price",
    "YearBuilt": "yearBuilt",
    
    # Location (🔥 NEW - properly mapped)
    "City": "city",
    "PostalCode": "zip",
    "StateOrProvince": "state",
    "Latitude": "latitude",
    "Longitude": "longitude",
    
    # Status
    "MlsStatus": "status",
    "StandardStatus": "standardStatus",
    "PropertyType": "propertyType",
}


def clean_property(raw_property: Dict) -> Dict:
    """
    Convert raw MLS-style data into MLS-safe clean data.
    
    🔥 UPDATED: Now handles real MLS Grid API field names
    """

    clean_data = {}

    for raw_key, clean_key in FIELD_MAPPING.items():
        if raw_key in raw_property:
            value = raw_property[raw_key]
            
            # Special handling for bathrooms (combine full + half)
            if raw_key == "BathroomsFull":
                full_baths = value or 0
                half_baths = raw_property.get("BathroomsHalf", 0) or 0
                clean_data["bathrooms"] = full_baths + (half_baths * 0.5)
            
            # Use LivingArea if available, otherwise BuildingAreaTotal
            elif raw_key == "LivingArea":
                clean_data[clean_key] = value or raw_property.get("BuildingAreaTotal", 0)
            
            else:
                clean_data[clean_key] = value

    return clean_data


def clean_properties(raw_properties: List[Dict]) -> List[Dict]:
    """
    Clean a list of raw MLS properties.
    """
    cleaned_list = []

    for raw_property in raw_properties:
        cleaned = clean_property(raw_property)

        if cleaned:
            cleaned_list.append(cleaned)

    return cleaned_list