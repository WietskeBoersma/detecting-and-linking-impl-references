## In this script the SRU of officielebekendmakingen will be accessed. This is done by using the PyPublicaties created by Venema(2024). 
## There has been some modifications to make it fit with the boolean search terms. Also the meeting year can be filled in
import xml.etree.ElementTree as ET
import urllib.request
import requests
import os
import json
import re
import ast

base_url = "https://zoek.officielebekendmakingen.nl/zoeken/api/v1/documenten"

class OfficielePublicatie:
    def __init__(self):
        self.identifier = []
        self.title = []
        self.type = []
        self.language = []
        self.authority = []
        self.creator = []
        self.modified = []
        self.temporal = []
        self.spatial = []
        self.alternative = []
        self.date = []
        self.hasVersion = []
        self.source = []
        self.requires = []
        self.isPartOf = []
        self.isrequiredby = []
        self.isreplacedby = []
        self.hasPart = []
        self.subject = []
        self.available = []
        self.abstract = []
        self.publisher = []
        self.issued = []
        self.replaces = []
        self.aanhangsel = []
        self.aanhangselnummer = []
        self.adviesRvs = []
        self.bedrijfsnaam = []
        self.behandeldDossier = []
        self.betreft = []
        self.betreftopschrift = []
        self.betreftRegeling = []
        self.bijlage = []
        self.datumBrief = []
        self.datumIndiening = []
        self.datumOndertekening = []
        self.datumOntvangst = []
        self.datumTotstandkoming = []
        self.datumVergadering = []
        self.deurwaardersdossier = []
        self.documentstatus = []
        self.documenttitel = []
        self.dossiernummer = []
        self.dossiertitel = []
        self.effectgebied = []
        self.einddatum = []
        self.datumEindeReactietermijn = []
        self.eindpagina = []
        self.externeBijlage = []
        self.gebiedsmarkering = []
        self.gemeentenaam = []
        self.geometrie = []
        self.geometrie = []
        self.geometrielabel = []
        self.hectometernummer = []
        self.heeftMededeling = []
        self.hoofddocument = []
        self.huisnummer = []
        self.huisletter = []
        self.huisnummertoevoeging = []
        self.indiener = []
        self.handelingenitemnummer = []
        self.jaargang = []
        self.kadastraleSectie = []
        self.ketenid = []
        self.ligtInGemeente = []
        self.ligtInProvincie = []
        self.materieelUitgewerkt = []
        self.mededelingOver = []
        self.ondernummer = []
        self.ontvanger = []
        self.organisatietype = []
        self.perceelnummer = []
        self.persoonsgegevens = []
        self.plaatsTotstandkoming = []
        self.postcode = []
        self.postcodeHuisnummer = []
        self.provincie = []
        self.provincienaam = []
        self.publicatienummer = []
        self.publicatienaam = []
        self.besluitReferendabiliteit = []
        self.referentienummer = []
        self.rijkswetnummer = []
        self.bekendmakingBetreffendePlan = []
        self.startdatum = []
        self.startpagina = []
        self.straatnaam = []
        self.subrubriek = []
        self.sysyear = []
        self.sysnumber = []
        self.sysseqnumber = []
        self.terinzageleggingBG = []
        self.terinzageleggingOP = []
        self.typeVerkeersbesluit = []
        self.verdragnummer = []
        self.vereisteVanBesluit = []
        self.vergaderjaar = []
        self.verkeersbordcode = []
        self.versieinformatie = []
        self.versienummer = []
        self.vraagnummer = []
        self.waterschapsnaam = []
        self.wegcategorie = []
        self.weggebruiker = []
        self.wegnummer = []
        self.woonplaats = []
        self.zittingsdatum = []
        self.product_area = []
        self.content_area = []
        self.datumTijdstipWijzigingWork = []
        self.datumTijdstipWijzigingExpression = []
        self.url = []
        self.prefferedUrl = []
        self.itemUrl = []
        self.timestamp = []

    @classmethod
    def from_xml_element(
        cls, element: ET.Element, namespaces: dict
    ) -> "OfficielePublicatie":
        op = cls()
        for child in element.findall(".//*", namespaces):
            tag = cls.parse_namespaced_tag(child.tag)

            if tag not in op.__dict__:
                continue

            if child.attrib:
                key, value = list(child.attrib.items())[0]
                value_dict = {value: child.text.strip() if child.text else ""}
                op.__dict__[tag].append(value_dict)

            else:
                op.__dict__[tag].append(child.text.strip() if child.text else "")

        return op

    @staticmethod
    def parse_namespaced_tag(tag: str) -> str:
        return tag.split("}", 1)[-1] if "}" in tag else tag

    def __iter__(self):
        for key in self.__dict__:
            yield {key: getattr(self, key)}

    def __repr__(self):
        return f"<OfficielePublicatie identifier={self.identifier}, title={self.title}>"


def extract_meeting_year(filename: str) -> str | None:
    match = re.search(r"(\d{8})", filename)
    if match:
        year_range = match.group(1)
        start = year_range[:4]
        end = year_range[4:]
        return f"{start}–{end}"
    return None


def ontsluit_kamerstukken(query_part2, startRecord=1, maximumRecords=1000, meeting_year=None):
    # Connectiestring met basis parameters, waarbij al gefilterd wordt op 'officielepublicaties'
    url = "https://repository.overheid.nl/sru"
    params = {
        "operation": "searchRetrieve",
        "version": "2.0",
        "query": "c.product-area==officielepublicaties AND  w.publicatienaam='Kamerstuk' AND ",
        "startRecord": startRecord,
        "maximumRecords": maximumRecords,
        "recordSchema": "gzd",
    }

    if meeting_year:
        params["query"] += f"w.vergaderjaar='{meeting_year}' AND "

    # Als er een tweede deel voor de query is, voeg deze toe aan de originele query en vervang de query in de parameters
    if query_part2:
        params["query"] += query_part2

    # Voer de request uit
    response = requests.get(url, params=params, timeout=10)
    print(params["query"])
    # Controleer of de request gelukt is
    if response.status_code == 200:
        # Zet de response om naar een XML object (bytes)
        xml_data = response.content

        # Parse de XML vanuit bytes naar een ElementTree object
        root = ET.fromstring(xml_data)

        # Return het ElementTree object
        return root
    else:
        print(f"Request failed with status code: {response.status_code}")

def convert_to_sru_query(zoekterm: str) -> str:
    # Split op logische operatoren (AND, OR, NOT, NEAR)
    pattern = r"\s+(AND|OR|NOT|NEAR)\s+"
    tokens = re.split(pattern, zoekterm)
    sru_parts = []
    word_parts=[]

    for token in tokens:
        token = token.strip('()')
        if token.upper() in ["AND", "OR", "NOT", "NEAR"]:
            sru_parts.append(token.upper())
        else:
            # Split operand op woorden en voeg AND toe tussen elk woord
            words = token.strip('"').split()
            if words:
                for word in words:
                    word_parts.append(f'cql.textAndIndexes = {word}')
                
                sru_parts.append(" AND ".join(word_parts))

    return ' '.join(sru_parts)

def retrieve_publications(zoekterm, meeting_year=None, query_list=[], max_records=1000, start_record=1):
    query_part2 = convert_to_sru_query(zoekterm)
    
    # SRU-aanroep
    root = ontsluit_kamerstukken(query_part2, start_record, max_records, meeting_year)
    print(root)
    print()

    # XML namespaces
    namespaces = {
        "sru": "http://docs.oasis-open.org/ns/search-ws/sruResponse",
        "gzd": "http://standaarden.overheid.nl/sru",
    }

    # Extract resultaten
    ops = []
    for record in root.findall(".//sru:records/sru:record", namespaces):
        record_data = record.find(".//sru:recordData", namespaces)
        if record_data is not None:
            ob = OfficielePublicatie.from_xml_element(record_data, namespaces)
            ops.append(ob)
    
    print(f"Aantal opgehaalde publicaties voor '{zoekterm}':", len(ops))

    return ops[:50]

def strip_xml_to_text(xml_url):
    response = urllib.request.urlopen(xml_url)
    tree = ET.parse(response)

    # Parse the XML file
    root = tree.getroot()  # Get the root element from the ElementTree

    # Extract text and replace newline characters with a space
    extracted_text = (
        ET.tostring(root, encoding="utf8", method="text")
        .decode("utf-8")
        .replace("\n", " ")
    )

    return extracted_text

def retrieve_implicit_referred_docs(file):
    # extract meeting year from file name
    meeting_year = extract_meeting_year(file)

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    zoekterms = [ref["zoekterm"] for ref in data.get("references", []) if "zoekterm" in ref]
    results = {}

    for z in zoekterms:
        results[z] = retrieve_publications(z, meeting_year=meeting_year, max_records=50, start_record=1)

    return results


def save_results_to_json(results_dict, output_path):
    serializable_dict = {
        k: [
            {"identifier": op.identifier, "title": op.title}
            for op in v
        ] for k, v in results_dict.items()
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_dict, f, indent=2, ensure_ascii=False)

results = retrieve_implicit_referred_docs('pipeline/reconciliation/OB-reconciliation/boolean_search_terms/h-tk-20012002-4369-4373_recon.json')
save_results_to_json(results, 'recon_results_2001_22.json')
