import json
import csv
import os

input_folder = "reconciliation/boolean_search_terms"
input_file_query = "reconciliation_results_query.csv"
output_csv = "combined_recon_references.csv"

# completing the reconciliation-ready dataset with the generated search terms for each reference
with open(output_csv, "w", newline="", encoding="utf-8") as f_out:
    writer = csv.writer(f_out)
    # Header met nummering in de eerste kolom
    writer.writerow(["#", "minute_id", "reference_text", "reference_number", "reasoning", "zoekterm"])

    nummer = 1
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_path = os.path.join(input_folder, filename)

            if filename.endswith("_recon.json"):
                minute_id = filename[:-11]
            else:
                minute_id = filename.rsplit(".", 1)[0]

            with open(input_path, "r", encoding="utf-8") as f_in:
                data = json.load(f_in)

                for item in data.get("references", []):
                    writer.writerow([
                        nummer,
                        minute_id,
                        item.get("reference_text", ""),
                        item.get("reference_number", ""),
                        item.get("reasoning", ""),
                        item.get("zoekterm", "")
                    ])
                    nummer += 1

print(f"Alle JSON-bestanden zijn samengevoegd en genummerd in {output_csv}")


