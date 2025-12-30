from typing import Dict, List


FIELD_MAPPING = {
    "bedrooms": "bedrooms",
    "bathrooms": "bathrooms",
    "areaSqft": "areaSqft",
    "price": "price",
    "yearBuilt": "yearBuilt",
    "city": "city",
    "zip": "zip",
    "latitude": "latitude",
    "longitude": "longitude",
    "propertyType": "propertyType",
    "status": "status"
}


def clean_property(raw_property: Dict) -> Dict:
    """
    Convert raw MLS-style data into MLS-safe clean data.
    """

    clean_data = {}

    for raw_key, clean_key in FIELD_MAPPING.items():
        if raw_key in raw_property:
            clean_data[clean_key] = raw_property[raw_key]

    return clean_data


def clean_properties(raw_properties: List[Dict]) -> List[Dict]:
    cleaned_list = []

    for raw_property in raw_properties:
        cleaned = clean_property(raw_property)

        if cleaned:
            cleaned_list.append(cleaned)

    return cleaned_list
