# this script calculates the hit@1 score for the SerpAPI method
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
            "minute_id": row.get("minute_id"),
            "paragraph": row.get("paragraph")
        })

# helper functies

def extract_words(term):
    # only match words and digits, no booleans or symbols
    return re.findall(r'\b\w+\b', term)

def filter_booleans(words):
    booleans = {'and', 'or', 'not'}
    return [w for w in words if w.lower() not in booleans]

def tokenize(text):
    words = extract_words(text)  # take all words and numbers out
    filtered = filter_booleans(words)  # delete Booleans
    return set(w.lower() for w in filtered)

# calculate the overlap
def overlap_ratio(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

# ======================================

hits = 0
total = 0
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

    term_tokens = tokenize(search_term)
    best_match = None
    best_score = 0

    for gold in true_data:
        gold_sentence = gold["sentence"]
        gold_min = gold["minute_id"]
        
        sentence_tokens = tokenize(gold_sentence)
        score = overlap_ratio(term_tokens, sentence_tokens)

        if not gold["external_identifier"] or not pred_id:
            continue

        if gold["external_identifier"] == pred_id and score > best_score and pred_min == gold_min:
            best_score = score
            best_match = gold

    if best_match:
        return 1, pred_id if pred_id else "" 
    else:
        return 0, pred_id if pred_id else ""

# adding new columns
if "hit-at-1-doc-serpapi-2" not in df_pred.columns:
    df_pred["hit-at-1-doc-serpapi-2"] = pd.NA
if "predicted_first_document-serpapi-2" not in df_pred.columns:
    df_pred["predicted_first_document-serpapi-2"] = ""

for idx, row in df_pred.iterrows():
    search_term = row["zoekterm_google"]
    hit, pred_doc = get_hit_and_predicted_doc(search_term)
    df_pred.at[idx, "hit-at-1-doc-serpapi-2"] = hit
    df_pred.at[idx, "predicted_first_document-serpapi-2"] = pred_doc

    hits += hit
    total += 1

hit_at_1 = hits / total if total > 0 else 0.0
print(f"Hit@1 (beste overlap én juiste dossier): {hit_at_1:.2%} ({hits} van {total})")

# first every seperate json file is turned into a csv file, then all files are combined using formatting.py
df_pred.to_csv("df_4.csv", index=False)

