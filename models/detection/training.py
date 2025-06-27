import csv
import json
from openai import OpenAI
import re 

client = OpenAI(
  api_key="API_KEY"
  )
# the gold standard dataset
true_refs = "gold_standard"
# training data file for a single meeting minute
output_file = "training_data" 

## extracts reference number from training data, because this is not given explicitly
def extract_reference_number(text):
    text = text.replace('\xa0', ' ')

    # Match explicit reference formats
    match = re.search(r'\b(\d{4,6}),?\s*nr\.?\s*\d+\b', text, re.IGNORECASE)
    if match:
        return match.group(0) 

    match = re.search(r'\b(?:kst-)?(\d{2,6}(?:\s?\d{2,6})?)\b', text)
    if match:
        return match.group(1).replace(" ", "") 

    return None

def generate_reasoning(sentence, reference_text):
    prompt = (
        f"Sentence: \"{sentence}\"\n"
        f"Reference: \"{reference_text}\"\n"
        f"**Shortly** explain why this is a reference to a parliamentary document, dossier, or third-party material. "
        f"Return a **short** explanation in English."
    )
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You explain references in Dutch parliamentary meeting minutes."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    
    return response.choices[0].message.content.strip()


with open(true_refs, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
    true_data = csv.DictReader(f_in)
    
    for row in true_data:
        if row.get("task_id") not in ["19", "20"]:  # Filter out task_id of doc that is getting tested
            true_segment = row["text"]
            sentence = row["sentence"]
            reasoning = generate_reasoning(sentence, true_segment)
            
            data = {
                "messages": [
                    {
                        "role": "user",
                        "content": f'Extract any implicit or explicit references to parliamentary documents from the following sentence. Return the output in JSON with fields: reference_text, reference_number, and reasoning.\n\nSentence: {sentence}'
                    },
                    {
                        "role": "assistant",
                        "content": json.dumps({
                            "reference_text": true_segment,
                            "reference_number": extract_reference_number(true_segment),
                            "reasoning": reasoning
                        }, ensure_ascii=False)
                    }
                ]
            }

            json_line = json.dumps(data, ensure_ascii=False)
            f_out.write(json_line + "\n")
