from bs4 import BeautifulSoup
from openai import OpenAI
import json

client = OpenAI(
  api_key="API_KEY"
  )

# Load & clean HTML file
def load_html_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    text = soup.get_text(separator="\n") 
    return text

# Ask the model to find references
def extract_references(text):
    system_prompt = (
        """"
            You are an expert assistant analyzing Dutch parliamentary meeting minutes. Your task is to detect all references to other documents, both explicit (e.g. with dossier numbers) and implicit (requiring contextual interpretation).

            == Annotation Guidelines ==
            - Include full noun phrases: e.g. "de aangegeven motie", not just "motie".
            - Exclude general or vague references like "beleid", "akkoord", "schriftelijke vragen".
            - Exclude plural references ("de ingediende moties") and references to future or unpublished documents.
            - Ignore references to third-party events (e.g., "de aanslag in Straatsburg").

            Each reference must include:
            - The full quoted reference text
            - The line number (if available)
            - If the reference is accompanied by a number this should be taken as the reference_number, otherwise the number is null
            - A short explanation of the reasoning, including useful linking details (e.g., law names, motion numbers, abbreviations, relevant MPs, political context, etc.)

            == Output Format ==
            {
            "references": [
                {
                "reference_text": "...",
                "reference_number": "...",
                "reasoning": "..."
                }
            ]
            }

            Detect **all** references, especially implicit ones.
        """
    )


    user_prompt = f"Analyze the document below:\n\n{text}"

    response = client.chat.completions.create(
        model="FINE_TUNED_MODEL",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    # Extract JSON part from the response
    content = response.choices[0].message.content
    try:
        # Try to parse if it already gave JSON
        return json.loads(content)
    except json.JSONDecodeError:
        # If it returned text, but not JSON, extract manually
        return {"explicit_references": [], "implicit_references": [], "raw_response": content}

# === Save result to JSON file ===
def save_references_to_json(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Run the tool 
def main():
    input_html = "meeting_minute_html"
    output_json = "output_file"

    text = load_html_text(input_html)
    references = extract_references(text)

    print("References extracted and saved.")

    # Safely extract raw_response
    if "references" in references:
        total = len(references["references"])
        print(f"✅ Total references detected: {total}")
        pretty = json.dumps(references, indent=2, ensure_ascii=False)
        save_references_to_json(references, output_json)
    else:
        print("⚠️ No references detected or unexpected response format.")


if __name__ == "__main__":
    main()
