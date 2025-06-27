import serpapi
import re
import pandas as pd
import json

api_key = "API_KEY"
client = serpapi.Client(api_key=api_key)

def extract_identifier_from_url(url):
    # Regex pattern to find kst-XXXXX-XX in a URL
    match = re.search(r'kst-\d+-\d+', url)
    if match:
        return match.group(0)
    return None # Return None if no identifier is found

df = pd.read_csv('referenties_google_searchterms.csv')
structured_results_by_query = {}

for index, row in df.iterrows():
    minute_id = row["minute_id"]
    query = row["zoekterm_google"]

    # Define the parameters for the current search, including the dynamic tbs value
    params = {
        "api_key": "API_KEY",
        "engine": "google",
        "gl": "nl",
        "hl": "nl", 
        "num": 50,
        "safe": "active",
        "q": f'{query} site: https://zoek.officielebekendmakingen.nl',
    }

    print(f"\nSearching for: '{query}' (Minute ID: {minute_id})")
    try:
        search = client.search(params)
        raw_results = search["organic_results"] # Get the raw SerpAPI response
        print(raw_results)
        # Initialize an empty list for the current query's results
        current_query_results = []


        for i, res in enumerate(raw_results):
            link = res.get("link")
            # Extract identifier from the link
            identifier = extract_identifier_from_url(link) 

            if identifier:
                # Create the desired dictionary for this specific result
                extracted_item = {
                    "identifier": [identifier], 
                    "title": [res.get("title")]
                }
                current_query_results.append(extracted_item)

        structured_results_by_query[query] = current_query_results

    except Exception as e:
        print(f"An error occurred for query '{query}' (Minute ID: {minute_id}): {e}")

# --- Data Persistence ---
# Define the output filename for the processed JSON results
output_json_filename = "serpapi_results.json"

# Save the processed results to a JSON file
with open(output_json_filename, 'w', encoding='utf-8') as f:
    json.dump(structured_results_by_query, f, indent=4, ensure_ascii=False)

print(f"\nProcessed and structured search results have been saved to '{output_json_filename}'")

print("\n--- Process Complete ---")
print(f"Total number of unique queries processed: {len(structured_results_by_query)}")