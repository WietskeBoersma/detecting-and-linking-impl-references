import re
import pandas as pd

def smart_google_search_term(raw_term):
    # Delete outer quotation marks
    term = raw_term.strip('"')

    # Split on boolean operators AND, OR, NEAR
    parts = re.split(r'\bAND\b|\bOR\b|\bNEAR\b', term, flags=re.IGNORECASE)

    # Trim spaces per part
    parts = [p.strip().strip('"') for p in parts if p.strip()]

    # Are quotation marks needed?
    def quote_if_needed(s):
        # If there are two or more words extra quotation marks are used
        if len(s.split()) > 1:
            return f'"{s}"'
        else:
            return s

    # Apply quote_if_needed
    quoted_parts = [quote_if_needed(p) for p in parts]

    # Combine with white space
    combined = " ".join(quoted_parts)

    return combined

# Voorbeeld
zoekterm = '"moties AND notaoverleg AND initiatiefnota AND Ploumen AND Van Gerven AND Ellemeet AND Big Farma:niet gezond!"'
print(smart_google_search_term(zoekterm))
# Output: "initiatiefnota Ploumen" Van "Gerven" Ellemeet Big Farma

# df = pd.read_csv("reconciliation_database copy.csv")

# df["zoekterm_google"] = df["zoekterm"].apply(smart_google_search_term)
# df.to_csv("referenties_google_searchterms.csv", index=False)
