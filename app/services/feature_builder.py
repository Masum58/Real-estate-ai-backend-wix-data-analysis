from typing import List, Dict
from statistics import mean


class FeatureBuilder:
    """
    Builds AI-ready features from MLS comparables
    and user input.
    
    🔥 UPDATED: Now supports distance-based weighted averaging
    Closer properties have more influence on final price calculation
    """

    @staticmethod
    def build(comparables: List[Dict], condition_score: int) -> Dict:
        prices = []
        weights = []
        price_per_sqft = []

        for comp in comparables:
            price = comp.get("price")
            sqft = comp.get("areaSqft")
            weight = comp.get("_weight", 1.0)  # Get weight from comparable_selector

            if price and sqft and sqft > 0:
                prices.append(price)
                weights.append(weight)
                price_per_sqft.append(price / sqft)

        if not prices:
            raise ValueError("No valid comparable prices found")

        # 🔥 Weighted average - closer properties have more influence
        if weights and sum(weights) > 0:
            avg_price = sum(p * w for p, w in zip(prices, weights)) / sum(weights)
        else:
            avg_price = mean(prices)  # Fallback to equal weight if no weights

        avg_price_sqft = mean(price_per_sqft)

        # Condition multiplier (simple & explainable)
        condition_multiplier = 1 + ((condition_score - 5) * 0.03)

        adjusted_price = avg_price * condition_multiplier

        return {
            "total_comparables": len(prices),
            "average_price": round(avg_price),
            "average_price_per_sqft": round(avg_price_sqft, 2),
            "condition_score": condition_score,
            "condition_multiplier": round(condition_multiplier, 2),
            "adjusted_estimated_price": round(adjusted_price),
            "price_range": {
                "min": round(adjusted_price * 0.92),
                "max": round(adjusted_price * 1.08)
            }
        }



