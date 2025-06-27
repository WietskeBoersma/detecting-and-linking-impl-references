from openai import OpenAI
import json

## In this script the API of OpenAI is used again. Here, to create a good boolean search term to use for the search engines.
## After this, the json files are all ready to be queried. (e.g. ob_query.py is next)
# OpenAI API-sleutel instellen
client = OpenAI(
  api_key=""
  )

# Inlezen van JSON-bestand met referenties
input_file = 'detected_refs'
output_file = 'reconciliation_ready'

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

references = data["references"]

# Prompt voor het omzetten van referenties naar zoektermen
def generate_prompt(reference_text, reasoning):
    return f"""
        You are an assistant that transforms parliamentary references into queries for officiëlebekendmakingen.nl.

    Referentie: "{reference_text}"
    Redenering: "{reasoning}"

    Generate a short, clear Dutch search term or phrase that a researcher could use to find the relevant document or topic. Include keywords like "motion", "bill", "dossier number", or "law proposal" if appropriate.
    ONLY answer with a search term. Use Boolean operators such as AND, OR, NOT, NEAR where appropriate.
    """

# Verwerk elke referentie met een API-call
results = []
for ref in references:
    prompt = generate_prompt(ref["reference_text"], ref["reasoning"])

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    zoekterm = response.choices[0].message.content.strip()
    ref["zoekterm"] = zoekterm

# Opslaan in nieuw JSON-bestand
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Zoektermen toegevoegd {len(references)} en opgeslagen in: {output_file}")
