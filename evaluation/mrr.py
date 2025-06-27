import json
import csv
import re

# ===== helper functions =====

def extract_words(term):
    return re.findall(r'\b\w+\b', term)

def filter_booleans(words):
    booleans = {'and', 'or', 'not'}
    return [w for w in words if w.lower() not in booleans]

def tokenize(text):
    words = extract_words(text)
    filtered = filter_booleans(words)
    return set(w.lower() for w in filtered)

def overlap_ratio(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

# input: multiple search results files + corresponding task_ids from the gold dataset
# expects json structure
predicted_sources = [
    "all_search_results_reconciliation"
]

task_ids = ["18", "20", "21", "22"]

true_source = "gold_data"

# load gold data for selected task_ids
true_data_by_task = {tid: [] for tid in task_ids}
with open(true_source, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        tid = row.get("task_id")
        if tid in task_ids:
            true_data_by_task[tid].append({
                "external_identifier": row.get("external_identifier"),
                "sentence": row.get("sentence")
            })

# calculate MRR over all docs
reciprocal_ranks = []

for pred_file, task_id in zip(predicted_sources, task_ids):
    with open(pred_file, 'r', encoding='utf-8') as f:
        predicted_data = json.load(f)
    
    true_data = true_data_by_task[task_id]

    # Pre-tokenize all gold sentences for matching with search term
    for entry in true_data:
        entry["tokens"] = tokenize(entry["sentence"])

    for search_term, entries in predicted_data.items():
        search_tokens = tokenize(search_term)

        # Find gold entries with overlap across a threshold
        threshold = 0.2 
        matching_gold_ids = set()
        for entry in true_data:
            score = overlap_ratio(search_tokens, entry["tokens"])
            if score >= threshold:
                matching_gold_ids.add(entry["external_identifier"])

        # Predicted identifiers for this search term
        predicted_ids = [entry.get("identifier", [None])[0] for entry in entries if entry.get("identifier")]
        predicted_ids = predicted_ids[:50]

        # MRR calculation
        found = False
        for rank, pred_id in enumerate(predicted_ids, start=1):
            if pred_id in matching_gold_ids:
                reciprocal_ranks.append(1 / rank)
                found = True
                break
        
        if not found:
            reciprocal_ranks.append(0.0)

mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
print(f"Mean Reciprocal Rank (MRR) over {len(reciprocal_ranks)} search terms: {mrr:.4f}")