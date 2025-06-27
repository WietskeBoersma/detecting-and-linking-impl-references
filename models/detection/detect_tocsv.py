# this script is used to put all seperate json files with detected references in a single csv file
import json
import csv
import os

# folder that contains all JSON files with detected references
input_folder = "input_folder"

# output file name
output_csv = "output_csv"

with open(output_csv, "w", newline="", encoding="utf-8") as f_out:
    writer = csv.writer(f_out)
    writer.writerow(["#", "minute_id", "reference_text", "reference_number", "reasoning"])

    nummer = 1
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            # extracts minute_id from file_name
            minute_id = filename.rsplit(".", 1)[0] 
            input_path = os.path.join(input_folder, filename)

            with open(input_path, "r", encoding="utf-8") as f_in:
                data = json.load(f_in)

                for item in data.get("references", []):
                    writer.writerow([
                        nummer,
                        minute_id,
                        item.get("reference_text", ""),
                        item.get("reference_number", ""),
                        item.get("reasoning", ""),
                    ])
                    nummer += 1

print(f"Alle JSON-bestanden zijn samengevoegd en genummerd in {output_csv}")
