from typing import List, Dict


def attach_condition_score(
    cleaned_properties: List[Dict],
    condition_score: int
) -> List[Dict]:
    """
    Attach user-provided condition score (0–10)
    to each cleaned property.
    """

    enriched = []

    for prop in cleaned_properties:
        enriched_property = prop.copy()
        enriched_property["conditionScore"] = condition_score
        enriched.append(enriched_property)

    return enriched


def build_ai_input(enriched_properties: List[Dict]) -> Dict:
    """
    Build final AI-ready input structure.
    This is what will later be sent to OpenAI.
    """

    return {
        "comparables": enriched_properties,
        "totalComparables": len(enriched_properties)
    }
