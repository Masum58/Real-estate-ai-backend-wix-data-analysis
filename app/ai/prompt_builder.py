from typing import Dict
from app.models.subject_property import SubjectProperty


class PromptBuilder:
    """
    Builds a safe, MLS-compliant prompt for AI price estimation.
    """

    @staticmethod
    def build(subject: SubjectProperty, features: Dict) -> str:
        prompt = f"""
You are a real estate valuation assistant.

Analyze the subject property using the provided market features.
Do NOT mention MLS, addresses, listing IDs, or any private data.
Do NOT guarantee prices.

Subject Property:
- Bedrooms: {subject.bedrooms}
- Bathrooms: {subject.bathrooms}
- Square Footage: {subject.square_footage}
- Year Built: {subject.year_built}
- Condition Score (1–10): {subject.condition_score}

Market Signals:
- Number of comparable sales analyzed: {features['total_comparables']}
- Average sale price of comparables: ${features['average_price']}
- Average price per square foot: ${features['average_price_per_sqft']}
- Condition multiplier applied: {features['condition_multiplier']}

Estimated Value Range:
- Minimum: ${features['price_range']['min']}
- Maximum: ${features['price_range']['max']}

Task:
Write a clear, professional summary explaining the estimated market value range.
Explain how property condition and comparable sales influence the estimate.
Avoid technical language.
Limit the response to 4–6 sentences.
"""
        return prompt.strip()
