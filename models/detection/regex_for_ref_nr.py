import pandas as pd
import csv

# Laad CSV
df_pred = pd.read_csv('detection/detection_results.csv')

filtered_pred = df_pred[~df_pred['reference_number'].astype(str).str.match(r'^\d')]

# Sla overgebleven rijen op
filtered_pred.to_csv('gefilterd_bestand.csv', index=False)


# Laad CSV
df_gold = pd.read_csv("labelstudio/baseline_annotation_labelstudio.csv")

delete_explicit = df_gold['reference_type'].astype(str).str.match(r'^explicit', case=False)

# Nu kun je filteren met:
filtered_gold = df_gold[~delete_explicit]

# Sla op
filtered_gold.to_csv("gefilterd_bestand_gold.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)
