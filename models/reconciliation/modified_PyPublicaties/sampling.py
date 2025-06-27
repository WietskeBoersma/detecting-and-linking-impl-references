import random
import PyPublicaties as pp

# Generate yearsets from ’1994 -1995 ’ to ’2023 -2024 ’
start_year = 1994
end_year = 2023
yearsets = [f"{year}-{year+1} " for year in range(start_year,end_year+1)]

# Randomly choose a yearset
selected_yearset= random.choice (yearsets)
print ("Randomly selected yearset:", selected_yearset)

query_list = [
    'dt.type="Handelingen" NOT w.subrubriek=="Sluiting" NOT w.subrubriek=="Mededelingen" NOT w.subrubriek=="Opening" NOT dt.title="Mededelingen" AND w.vergaderjaar='
    + selected_yearset
]


pubs = pp.retrieve_publications(query_list=query_list, max_records=1000)
selected_number = random.randint(0, 999)

if pubs:
    random_minute = pubs[selected_number]
    print("Documents selected ✅")
    print(random_minute)
else:
    print("No publications were found for the given query.")