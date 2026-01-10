from typing import Dict, List


def analyze_price_locally(ai_input: Dict) -> Dict:
    """
    Local price analysis without OpenAI.
    Uses 1-mile radius methodology with distance-based weighting.
    Matches the logic in feature_builder.py
    """

    comparables: List[Dict] = ai_input["comparables"]
    subject = ai_input.get("subject", {})
    condition_score = subject.get("condition_score", 5)

    # Extract prices and weights
    prices = []
    weights = []
    
    for comp in comparables:
        price = comp.get("price")
        weight = comp.get("_weight", 1.0)
        
        if price and price > 0:
            prices.append(price)
            weights.append(weight)

    if not prices:
        return {
            "price_min": None,
            "price_max": None,
            "summary": "Not enough comparable data to estimate price."
        }

    # Weighted average (closer properties have more influence)
    if weights and sum(weights) > 0:
        avg_price = sum(p * w for p, w in zip(prices, weights)) / sum(weights)
    else:
        avg_price = sum(prices) / len(prices)

    # Condition adjustment (matches feature_builder.py)
    condition_multiplier = 1 + ((condition_score - 5) * 0.03)
    estimated_price = avg_price * condition_multiplier

    # Price range (±8% as per feature_builder.py)
    price_min = round(estimated_price * 0.92)
    price_max = round(estimated_price * 1.08)

    # Professional summary mentioning methodology
    total_comps = len(comparables)
    avg_price_formatted = f"${avg_price:,.0f}"
    
    summary = (
        f"The estimated market value range for the subject property is between "
        f"approximately ${price_min:,} and ${price_max:,}. This estimate is based on "
        f"analysis of {total_comps} comparable sales within a 1-mile radius of the property. "
        f"Properties closer to the subject property were weighted more heavily in the analysis, "
        f"with an average sale price of {avg_price_formatted}. "
    )
    
    if condition_score != 5:
        if condition_score > 5:
            summary += (
                f"The property's above-average condition (rated {condition_score}/10) "
                f"positively influences its value, with a condition multiplier of {condition_multiplier:.2f} applied. "
            )
        else:
            summary += (
                f"The property's below-average condition (rated {condition_score}/10) "
                f"negatively influences its value, with a condition multiplier of {condition_multiplier:.2f} applied. "
            )
    else:
        summary += (
            f"The property's average condition (rated {condition_score}/10) "
            f"is reflected in the standard market analysis. "
        )
    
    summary += (
        "This distance-based methodology ensures accurate neighborhood-level valuation."
    )

    return {
        "price_min": price_min,
        "price_max": price_max,
        "summary": summary
    }