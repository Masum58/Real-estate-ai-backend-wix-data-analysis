import os
import json
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_price_with_openai(ai_input: Dict) -> Dict:
    """
    Call OpenAI to generate price range and summary.
    Uses 1-mile radius methodology with distance-based weighting.
    """

    comparables: List[Dict] = ai_input["comparables"]
    subject = ai_input.get("subject", {})

    # Include distance and weight if available
    compact_comps = []
    for p in comparables:
        comp_data = {
            "beds": p.get("bedrooms"),
            "baths": p.get("bathrooms"),
            "sqft": p.get("areaSqft"),
            "price": p.get("price"),
            "yearBuilt": p.get("yearBuilt"),
        }
        
        # Include distance info if available
        if "_distance" in p:
            comp_data["distance_miles"] = round(p["_distance"], 2)
        if "_weight" in p:
            comp_data["weight"] = p["_weight"]
            
        compact_comps.append(comp_data)

    # Sort by distance (closest first)
    compact_comps.sort(key=lambda x: x.get("distance_miles", 999))

    prompt = f"""
You are a professional real estate valuation assistant.

METHODOLOGY:
- All comparables are within a 1-mile radius of the subject property
- Properties are sorted by distance (closest first)
- Closer properties have higher weight in the analysis
- This ensures neighborhood-level accuracy

Subject Property:
- Bedrooms: {subject.get('bedrooms', 'N/A')}
- Bathrooms: {subject.get('bathrooms', 'N/A')}
- Square Footage: {subject.get('square_footage', 'N/A')}
- Year Built: {subject.get('year_built', 'N/A')}
- Condition Score: {subject.get('condition_score', 'N/A')}/10

Comparable Properties (within 1 mile, sorted by distance):
{json.dumps(compact_comps, indent=2)}

Total Comparables: {len(compact_comps)}

RULES:
- Do NOT mention specific MLS addresses, listing IDs, or agent names
- Do NOT reference database or technical details
- DO mention the 1-mile radius methodology
- DO mention that closer properties influenced the estimate more
- DO explain how condition score affects value
- Use professional, neutral language

TASK:
1) Analyze the comparable sales data
2) Estimate a reasonable price range
3) Provide a professional summary explaining:
   - The 1-mile radius methodology
   - How many comparables were used
   - How property condition influences value
   - The market trends reflected

OUTPUT FORMAT (JSON only, no markdown):
{{
  "price_min": <number>,
  "price_max": <number>,
  "summary": "<professional explanation>"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # ✅ Fixed model name
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a professional real estate CMA specialist. "
                        "You analyze properties using 1-mile radius methodology with "
                        "distance-based weighting. Provide accurate, professional summaries."
                    )
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"}  # ✅ Force JSON response
        )

        content = response.choices[0].message.content
        
        # ✅ Safe JSON parsing (not eval!)
        result = json.loads(content)
        
        # Validate structure
        if not all(k in result for k in ["price_min", "price_max", "summary"]):
            raise ValueError("Invalid response structure")
            
        return result
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Raw content: {content}")
        return {
            "price_min": None,
            "price_max": None,
            "summary": "Unable to parse AI response. Please try again."
        }
        
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return {
            "price_min": None,
            "price_max": None,
            "summary": "Unable to generate price estimate at this time. Please try again."
        }