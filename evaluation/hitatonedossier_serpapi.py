import json
import csv
import re
import pandas as pd
import os

# all search results
predicted_source = "search_results"
# gold standard dataset
true_source = "gold_standard"
# output_file
predicted_reconciliation = "all_reconciliation_results"
df_pred = pd.read_csv(predicted_reconciliation)

with open(predicted_source, 'r', encoding='utf-8') as f:
    predicted_data = json.load(f)

true_data = []
with open(true_source, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        true_data.append({
            "external_identifier": row.get("external_identifier"),
            "sentence": row.get("sentence"),
            "minute_id": row.get("minute_id")
        })

print(f"Number of relevant gold entries loaded: {len(true_data)}")
#  helper functies

def extract_dossier(identifier):
    if not identifier or not isinstance(identifier, str):
        return None
    match = re.match(r'kst-(\d+)', identifier)
    return match.group(1) if match else None

def tokenize(text):
    if not text:
        return set()
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = {'and', 'or', 'not'}
    return set(w for w in words if w not in stopwords)

def overlap_ratio(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

# ====================================
hits = 0
total = 0
no_results = 0
matched_gold_sentences = set()  # set om unieke gold sentences te onthouden

def get_hit_and_predicted_doc(search_term):
    entries = predicted_data.get(search_term, [])
    first_entry = entries[0] if entries else None
    pred_id = None
    if first_entry:
        ids = first_entry.get("identifier", [])
        if ids:
            pred_id = ids[0]
            pred_min = first_entry.get("minute_id", [])
            pred_min = pred_min[0]
    
    pred_dossier = extract_dossier(pred_id)

    term_tokens = tokenize(search_term)
    best_match = None
    best_score = 0

    for gold in true_data:
        gold_sentence = gold["sentence"]
        gold_min = gold["minute_id"]

        if gold_sentence in matched_gold_sentences:
            # deze zin is al gematcht
            continue  
        

        sentence_tokens = tokenize(gold_sentence)
        score = overlap_ratio(term_tokens, sentence_tokens)
        gold_dossier = extract_dossier(gold["external_identifier"])

        if not gold_dossier or not pred_dossier:
            continue
        
        if gold_dossier == pred_dossier and score > best_score and gold_min == pred_min:
            best_score = score
            best_match = gold

    if best_match:
        matched_gold_sentences.add(best_match["sentence"])
        return 1
    else:
        return 0


hit_at_1 = hits / total if total > 0 else 0.0
print(f"Hit@1 (beste overlap én juiste dossier): {hit_at_1:.2%} ({hits} van {total})")
print(f"Search terms with no result: {no_results}")

# Nieuwe kolommen toevoegen

if "hit-at-1-dossier-serpapi-2" not in df_pred.columns:
    df_pred["hit-at-1-dossier-serpapi-2"] = pd.NA


for idx, row in df_pred.iterrows():
    search_term = row["zoekterm_google"]
    hit = get_hit_and_predicted_doc(search_term)
    df_pred.at[idx, "hit-at-1-dossier-serpapi-2"] = hit

    hits += hit
    total += 1

hit_at_1 = hits / total if total > 0 else 0.0
print(f"Hit@1 (beste overlap én juiste dossier): {hit_at_1:.2%} ({hits} van {total})")

# first every seperate json file is turned into a csv file, then all files are combined using formatting.py
df_pred.to_csv("df_new2.csv", index=False)