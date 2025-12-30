from services.mls_service import fetch_raw_properties
from compliance.output_cleaner import clean_properties
from services.ai_service import attach_condition_score, build_ai_input
from services.openai_price_analyzer import analyze_price_with_openai
from services.backend_poster import post_to_client_backend


def main():
    raw_data = fetch_raw_properties()
    cleaned_data = clean_properties(raw_data["items"])

    condition_score = 7

    enriched = attach_condition_score(cleaned_data, condition_score)
    ai_input = build_ai_input(enriched)

    ai_result = analyze_price_with_openai(ai_input)

    payload = {
        "comparables": cleaned_data,
        "ai_result": ai_result
    }

    success = post_to_client_backend(payload)

    if success:
        print("Data successfully sent to client backend.")
    else:
        print("Failed to send data to client backend.")


if __name__ == "__main__":
    main()
