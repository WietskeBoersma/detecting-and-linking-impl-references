from bs4 import BeautifulSoup
from openai import OpenAI
import json

client = OpenAI(
  api_key="API_KEY"
  )


# Load and clean HTML file
def load_html_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    text = soup.get_text(separator="\n")
    return text

# Ask the model to find references 
def extract_references(text):
    system_prompt = (
        "You are an expert assistant that analyzes meeting minutes of the Dutch parliament.\n"
        "Your purpose is to detect references to other documents from these meeting minutes.\n"
        "These references can be explicit (supported by a document/dossier number), as well as implicit. \n"
        "If a reference is implicit, interpretation of the context is compulsory.\n"
        "This requires very careful and precise reading and interpretation of the document from you. \n"
        "As well as expertise in reading and comprehending the Dutch language.\n"
        "Your expertise in this particular case is detecting ALL references, but especially those that refer to other parliamentary documents.\n"

        "It is important for you to write each and every one of these down and put them in them in the JSON file.\n"
        "These type of references are often recognized by the presence of a referring word before them (e.g. 'deze', 'die', 'mijn')"

        "== Annotation Rules ==\n"
        "- Preserve articles and adjectives: annotate 'de aangegeven motie', not just 'motie'.\n"
        "- Exclude general terms like 'beleid', 'akkoord', 'schriftelijke vragen'.\n"
        "- Exclude plural references ('de ingediende moties') and future/unpublished items.\n"
        "- Exclude references to documents that will be written in the future or that are not yet published, recognize them by the context surrounding them.\n"
        "- Do not annotate third-party *events* (e.g., 'de aanslag in Straatsburg').\n\n"

        "Accompany all references with reasoning that includes all useful linking details:\n"
        "- Names of laws or documents\n"
        "- Dates\n"
        "- Motion numbers\n"
        "- Names of MPs\n"
        "- Parliamentary session details\n"
        "- Political topics or dossier titles\n"
        "- Any abbreviations or Dutch document codes (e.g. Kamerstuk 35 928)\n"

        "== Output Format ==\n"
        "Each reference must include the exact text of the reference: the sentence in which the reference appears and if it is accompanied by a number this is the reference_number, otherwise the number is None.\n"
        "Return a JSON object:\n"
        "{\n"
        "  \"references\": [{\"reference_text\": \"...\", \"reference_number\": \"...\", \"reasoning\":\"...\"],\n"
        "}\n"
       
       
        "Please make sure to detect all references also those that are not explicit (document/dossiernumber)"
    )


    user_prompt = f"Analyze the document below:\n\n{text}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2  # keep it focused
    )

    # Extract JSON part from the response
    content = response.choices[0].message.content
    try:
        # Try to parse if the model already gave JSON
        return json.loads(content)
    except json.JSONDecodeError:
        # If it returned text, but not JSON, extract manually (fallback)
        return {"explicit_references": [], "implicit_references": [], "raw_response": content}

# Save result to JSON file 
def save_references_to_json(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Run the tool
def main():
    # Put a parliamentary meeting minute as input
    input_html = "input_file" 
    # name for the output file
    output_json = "output_file"

    text = load_html_text(input_html)
    references = extract_references(text)

    print("References extracted and saved.")

    # Safely extract raw_response
    raw_response = references.get("raw_response", "")

# Clean and parse the JSON content
    if raw_response.startswith("```json"):
        raw_response = raw_response.strip("```json").strip("```").strip()

    try:
        parsed = json.loads(raw_response)
        total = len(parsed.get("references", []))
        print(f"✅ Total references detected: {total}")
        pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
        save_references_to_json(parsed, output_json)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)

if __name__ == "__main__":
    main()
