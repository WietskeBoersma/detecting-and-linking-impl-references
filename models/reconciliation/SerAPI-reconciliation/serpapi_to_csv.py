import pandas as pd
import json
import os

# adding minute ids to json files to make splitting per meeting minute possible
json_input_file_path = 'serpapi_results.json' 
csv_file_path = 'referenties_google_searchterms.csv' 
json_output_file_path = 'serpapi_results_with_minute_ids.json'

df_references = pd.read_csv(csv_file_path)
zoekterm_to_minute_id_map = df_references.set_index('zoekterm_google')['minute_id'].to_dict()

print(f"CSV-bestand '{csv_file_path}' succesvol geladen en mapping gemaakt.")
print(f"Aantal unieke zoektermen in CSV voor mapping: {len(zoekterm_to_minute_id_map)}")

with open(json_input_file_path, 'r', encoding='utf-8') as f:
    search_results_data = json.load(f)
print(f"JSON-invoerbestand '{json_input_file_path}' succesvol geladen.")

updated_search_results = {}
matches_found = 0
results_processed_count = 0

print("\nBeginnen met het verrijken van de JSON-resultaten met minute_ids...")
for search_term_key, results_list in search_results_data.items():
    associated_minute_id = zoekterm_to_minute_id_map.get(search_term_key)

    if associated_minute_id:
        matches_found += 1
        enriched_results_for_term = []
        if results_list: #
            for result_item in results_list:
                # Add  minute_id to each individual result 
                enriched_item = result_item.copy()
                enriched_item['minute_id'] = [associated_minute_id]
                enriched_results_for_term.append(enriched_item)
                results_processed_count += 1
        updated_search_results[search_term_key] = enriched_results_for_term
    else:
        updated_search_results[search_term_key] = results_list
        print(f"  Waarschuwing: Geen 'minute_id' gevonden in CSV voor zoekterm: '{search_term_key}'. Originele resultaten overgenomen.")

print(f"\nVerrijking voltooid.")
print(f"Aantal zoektermen in JSON gematcht met minute_id: {matches_found}")
print(f"Totaal aantal individuele zoekresultaten (identifier/title paren) verrijkt: {results_processed_count}")


# Save adjusted json file
try:
    with open(json_output_file_path, 'w', encoding='utf-8') as f:
        json.dump(updated_search_results, f, indent=4, ensure_ascii=False)
    print(f"\nBijgewerkte JSON-output opgeslagen als '{json_output_file_path}'.")
except Exception as e:
    print(f"Fout bij het opslaan van het bijgewerkte JSON-bestand: {e}")

print("\n--- Proces compleet ---")