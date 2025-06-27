from structure import OfficielePublicatie
from webservice import ontsluit_handelingen

def retrieve_publications(query_list = [], max_records = 1000, start_record = 1):
    query_concatter = ' AND '
    query_part2 = ' AND dt.date >= "1999-01-01" AND dt.date <= "2025-01-01"'
    for value in query_list:
        query_part2 += f"{query_concatter}{value}"
    
    root = ontsluit_handelingen(query_part2, start_record, max_records)
    
    namespaces = {
    'sru': "http://docs.oasis-open.org/ns/search-ws/sruResponse",
    'gzd': "http://standaarden.overheid.nl/sru"
    }
    
    ops = []
    # Loop door iedere record in de records container
    for record in root.findall('.//sru:records/sru:record', namespaces):
        # Genest in <sru:recordData>
        record_data = record.find('.//sru:recordData', namespaces)
        if record_data is not None:
            ob = OfficielePublicatie.from_xml_element(record_data, namespaces)
            ops.append(ob)
            
    return ops


print(retrieve_publications())

EXCLUDED_TYPES = ["Opening", "Sluiting", "Mededelingen", "Aanhangsel"]

def is_relevant(op):
    # Voorbeeld: check of een uitgesloten woord voorkomt in de titel
    title = op.title[0] if op.title else ""
    return not any(excl.lower() in title.lower() for excl in EXCLUDED_TYPES)

def retrieve_filtered_publications(query_list=[], max_records=10, start_record=1):
    ops = retrieve_publications(query_list, max_records, start_record)
    filtered_ops = [op for op in ops if is_relevant(op)]
    return filtered_ops

print(retrieve_filtered_publications())