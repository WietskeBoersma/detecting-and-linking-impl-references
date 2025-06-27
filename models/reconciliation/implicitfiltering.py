import json
import re

# This script is used to delete the numbers from the explicit references, so these can be used as extra evaluation data
# The next script creates boolean search terms of what is left: booleantranslator.py
# Input and output file paths
input_file = 'detection_results'
output_file = 'output'

# Load the JSON data
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

references = data.get("references", [])

number_pattern = re.compile(r'\d+')
bracket_pattern = re.compile(r'\([^)]*\)')

def clean_text_field(text):
    if not text:
        return ""
    # eerst haakjesinhoud verwijderen
    text = bracket_pattern.sub('', text)

    # dan alle getallen verwijderen
    text = number_pattern.sub('', text)   
    return text.strip()

keywords = [
    "motie", "wetsvoorstel", "voorstel van wet", "nota", "beleidsnota",
    "kamerstuk", "brief", "verslag", "toelichting",
    "initiatiefnota", "notaoverleg", "amendement", "wet"
]

disallowed_keywords = [
    "algemeen overleg", "schriftelijke vragen", "beleid", "akkoord", 'agendapunt'
]

def is_parliamentary_doc(reference):
    reference_text = reference.get("reference_text", "").lower()
    zoekterm = reference.get("zoekterm", "").lower()
    allowed = any(keyword in reference_text or keyword in zoekterm for keyword in keywords)

    # Check op uitgesloten woorden
    disallowed = any(banned in reference_text or banned in zoekterm for banned in disallowed_keywords)

    return allowed and not disallowed

filtered_references = []
for ref in references:
    if is_parliamentary_doc(ref):
        cleaned_ref = ref.copy()
        cleaned_ref["reference_text"] = clean_text_field(cleaned_ref.get("reference_text", ""))
        cleaned_ref["zoekterm"] = clean_text_field(cleaned_ref.get("zoekterm", ""))
        cleaned_ref["reasoning"] = clean_text_field(cleaned_ref.get("reasoning", ""))
        filtered_references.append(cleaned_ref)

# Sla de gefilterde verwijzingen op
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({"references": filtered_references}, f, ensure_ascii=False, indent=2)

print(f"✅ Filtered {len(filtered_references)} implicit references saved to: {output_file}")
