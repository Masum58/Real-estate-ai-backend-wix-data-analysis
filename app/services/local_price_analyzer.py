from typing import Dict, List


def analyze_price_locally(ai_input: Dict) -> Dict:
    """
    Local price analysis without OpenAI.
    This simulates AI behavior for testing.
    """

    comparables: List[Dict] = ai_input["comparables"]
    condition_score: int = comparables[0]["conditionScore"]

    prices = [prop["price"] for prop in comparables if "price" in prop]

    if not prices:
        return {
            "price_min": None,
            "price_max": None,
            "summary": "Not enough data to estimate price."
        }

    avg_price = sum(prices) / len(prices)

    # Condition adjustment logic (simple, safe)
    condition_multiplier = 1 + ((condition_score - 5) * 0.02)

    estimated_price = avg_price * condition_multiplier

    price_min = round(estimated_price * 0.95)
    price_max = round(estimated_price * 1.05)

    summary = (
        "Based on recent nearby sales and the provided property condition, "
        "the estimated market value falls within a reasonable price range."
    )

    return {
        "price_min": price_min,
        "price_max": price_max,
        "summary": summary
    }
