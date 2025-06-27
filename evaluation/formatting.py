# this script is for formatting all reconciliation results together in one csv
import pandas as pd

# reading the datasets
df1 = pd.read_csv('df_1')
df2 = pd.read_csv('df_2')
df3 = pd.read_csv('df_2')

# combine all rows
combined = pd.concat([df1, df2, df3], ignore_index=True)

# save
combined.to_csv("all_results", index=False)

# put in the csv file with all reconciliation results
df = pd.read_csv('reconciliation_results')

df_improved = df.groupby('zoekterm').agg(lambda x: x.dropna().iloc[0] if not x.dropna().empty else None).reset_index()

print("Originele kolomvolgorde:")
print(df_improved.columns.tolist())

correct_order = ['#', 'minute_id', 'reference_text', 'reference_number', 'reasoning', 'zoekterm', 'zoekterm_google', 'hit-at-1-doc', 'hit-at-1-doc-serpapi', 'hit-at-1-dossier', 'hit-at-1-dossier-serpapi', 'predicted_first_document', 'predicted_first_document-serpapi',]

df_new_order = df_improved[correct_order]
df_new_order.sort_values(by='#', ascending=True, inplace=True)

print("\nNieuwe kolomvolgorde (alles gespecificeerd):")
print(df_new_order.columns.tolist())

df_new_order.to_csv('recon_results_2.csv', index=False)
