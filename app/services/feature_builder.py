from typing import List, Dict
from statistics import mean


class FeatureBuilder:
    """
    Builds AI-ready features from MLS comparables and user input.
    
    🔥 UPDATED: Distance-based weighted averaging methodology
    - Closer properties have more influence on final price
    - 1-mile radius comparable selection
    - Industry-standard CMA calculations
    """

    @staticmethod
    def build(comparables: List[Dict], condition_score: int) -> Dict:
        """
        Calculate price features from comparable properties.
        
        Args:
            comparables: List of comparable properties with prices, sqft, and weights
            condition_score: Property condition rating (1-10)
            
        Returns:
            Dictionary with price analysis and valuation range
        """
        prices = []
        weights = []
        price_per_sqft = []

        for comp in comparables:
            price = comp.get("price")
            sqft = comp.get("areaSqft")
            weight = comp.get("_weight", 1.0)  # Distance-based weight from comparable_selector

            if price and sqft and sqft > 0:
                prices.append(price)
                weights.append(weight)
                price_per_sqft.append(price / sqft)

        if not prices:
            raise ValueError("No valid comparable prices found")

        # 🔥 Weighted average price - closer properties have MORE influence
        if weights and sum(weights) > 0:
            avg_price = sum(p * w for p, w in zip(prices, weights)) / sum(weights)
            avg_price_sqft = sum(pps * w for pps, w in zip(price_per_sqft, weights)) / sum(weights)
        else:
            # Fallback to equal weight if no weights available
            avg_price = mean(prices)
            avg_price_sqft = mean(price_per_sqft)

        # Condition multiplier (industry standard: 3% per point from baseline of 5)
        # Example: Condition 8 = 1.09x multiplier (9% increase)
        # Example: Condition 3 = 0.94x multiplier (6% decrease)
        condition_multiplier = 1 + ((condition_score - 5) * 0.03)

        # Apply condition adjustment
        adjusted_price = avg_price * condition_multiplier

        # Price range: ±8% (industry standard confidence interval)
        return {
            "total_comparables": len(prices),
            "average_price": round(avg_price),
            "average_price_per_sqft": round(avg_price_sqft, 2),
            "condition_score": condition_score,
            "condition_multiplier": round(condition_multiplier, 2),
            "adjusted_estimated_price": round(adjusted_price),
            "price_range": {
                "min": round(adjusted_price * 0.92),  # -8%
                "max": round(adjusted_price * 1.08)   # +8%
            }
        }