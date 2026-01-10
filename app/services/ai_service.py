from typing import List, Dict, Optional


def build_ai_input(
    subject_property: Dict,
    comparable_properties: List[Dict]
) -> Dict:
    """
    Build AI-ready input structure for valuation.
    
    Args:
        subject_property: The property being valued (with condition_score)
        comparable_properties: List of comparable sales (each with own condition)
        
    Returns:
        Dictionary ready for AI analysis
    """
    
    return {
        "subject": {
            "address": subject_property.get("address"),
            "city": subject_property.get("city"),
            "state": subject_property.get("state"),
            "zip_code": subject_property.get("zip_code"),
            "bedrooms": subject_property.get("bedrooms"),
            "bathrooms": subject_property.get("bathrooms"),
            "square_footage": subject_property.get("square_footage"),
            "year_built": subject_property.get("year_built"),
            "condition_score": subject_property.get("condition_score")
        },
        "comparables": comparable_properties,
        "total_comparables": len(comparable_properties),
        "methodology": {
            "radius": "1 mile maximum",
            "weighting": "Distance-based (closer = higher weight)",
            "sorting": "By proximity (closest first)"
        }
    }


# Legacy function - DO NOT USE
def attach_condition_score(
    cleaned_properties: List[Dict],
    condition_score: int
) -> List[Dict]:
    """
    DEPRECATED: This function is no longer used.
    Condition scores should come from individual property data.
    """
    print("⚠️ Warning: attach_condition_score is deprecated!")
    return cleaned_properties