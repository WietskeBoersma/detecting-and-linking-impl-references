import json
import csv
import re
import os
import pandas as pd

# Load predicted references csv and the gold dataset
input_csv = "predictions_csv"
true_refs_path = "gold_csv"

# Read predicted references csv
df = pd.read_csv(input_csv)

# Group by minute_id
grouped = df.groupby("minute_id")

pattern = re.compile(r'\b\w+\b')
# load baseline annotations into a dictionary: minute_id -> list of word sets for each segment
true_segments_by_task = {}
with open(true_refs_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # skip the overly long debate from evaluation
        if row.get("minute_id") == "h-tk-20022003-3055-3080":
            continue

        minute_id = row.get("minute_id")
        text = row.get("text")
        if minute_id and text:
            # extract unique words from the text segment
            tokens = set(pattern.findall(text))
             # append word set to the list for this minute_id
            true_segments_by_task.setdefault(minute_id, []).append(tokens)

# helper functies
# extracting minute_id from filename, this will be used to match the gold and predicted
def extract_minute_id_from_filename(filename):
    return os.path.splitext(os.path.basename(filename))[0]

# loading the predicted references
def load_pred_segments(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        segments = []
        for ref in data.get("references", []):
            text = ref.get("reference_number") or ref.get("reference_text")
            segments.append(set(pattern.findall(text)) if text else set())
        return segments

# calculate TP, FP, FN based on overlap of predicted and true tokens
def word_overlap_metrics(pred_segment: set, true_segment: set):
    tp = len(pred_segment & true_segment)
    fp = len(pred_segment - true_segment)
    fn = len(true_segment - pred_segment)
    return tp, fp, fn

# compute F1 score with protection against division by zero
def f1_score(tp, fp, fn):
    denom = 2 * tp + fp + fn
    return (2 * tp) / denom if denom > 0 else 0

def panoptic_quality(pred_segments, true_segments):
    matched = []
    sum_f1 = 0

    # find matches between predicted and true segments with TP > FP and TP > FN
    for t_idx, true_seg in enumerate(true_segments):
        for h_idx, pred_seg in enumerate(pred_segments):
            tp, fp, fn = word_overlap_metrics(pred_seg, true_seg)
            if tp > fp and tp > fn:
                f1 = f1_score(tp, fp, fn)
                matched.append((h_idx, t_idx, f1))

    matched_pairs = []
    used_preds = set()
    used_trues = set()

     # greedy matching by highest F1, avoiding duplicate matches
    for h_idx, t_idx, f1 in sorted(matched, key=lambda x: -x[2]):
        if h_idx not in used_preds and t_idx not in used_trues:
            matched_pairs.append((h_idx, t_idx, f1))
            sum_f1 += f1
            used_preds.add(h_idx)
            used_trues.add(t_idx)

    TP = len(matched_pairs)
    FP = len(pred_segments) - TP
    FN = len(true_segments) - TP

    return sum_f1, TP, FP, FN

# check if predicted tokens match any true segment for this minute
def is_true_positive(minute_id, pred_tokens):
    true_segments = true_segments_by_task.get(minute_id, [])
    for true_tokens in true_segments:
        tp, fp, fn = word_overlap_metrics(pred_tokens, true_tokens)
        if tp > fp and tp > fn:
            return 1
    return 0

# add TP flag per predicted reference in df
tp_flags = []
for _, row in df.iterrows():
    minute_id = row["minute_id"]
    text = row["reference_number"] if pd.notna(row["reference_number"]) else row["reference_text"]
    tokens = set(pattern.findall(str(text))) if text else set()
    tp_flags.append(is_true_positive(minute_id, tokens))

df["TP"] = tp_flags

# accumulate total metrics over all groups (minute_id)
total_f1_sum = 0
total_tp = 0
total_fp = 0
total_fn = 0

for minute_id, group in grouped:
    pred_segments = []
    for _, row in group.iterrows():
        text = row["reference_number"] if pd.notna(row["reference_number"]) else row["reference_text"]
        tokens = set(pattern.findall(text)) if text else set()
        pred_segments.append(tokens)

    true_segments = true_segments_by_task.get(minute_id, [])
    if not true_segments:
        print(f"Geen correcte segmenten gevonden voor minute_id: {minute_id}")
        continue

    sum_f1, TP, FP, FN = panoptic_quality(pred_segments, true_segments)

    denom = TP + 0.5 * FP + 0.5 * FN
    pq = sum_f1 / denom if denom > 0 else 0
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0

    total_f1_sum += sum_f1
    total_tp += TP
    total_fp += FP
    total_fn += FN

# calculate overall metrics across all documents
total_denom = total_tp + 0.5 * total_fp + 0.5 * total_fn
total_pq = total_f1_sum / total_denom if total_denom > 0 else 0
total_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
total_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0

print("\n==========================")
print(" TOTALE RESULTATEN OVER ALLE DOCUMENTEN")
print(f"  TP={total_tp}, FP={total_fp}, FN={total_fn}")
print(f"  Panoptic Quality: {total_pq:.3f}")
print(f"  Precision: {total_precision:.3f}")
print(f"  Recall: {total_recall:.3f}")

# csv of the detected references and a column 'TP' indicating whether it was a correct reference or not
df.to_csv("results_csv", index=False)