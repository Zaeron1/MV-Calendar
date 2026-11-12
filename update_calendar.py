import os
import re
import requests
from icalendar import Calendar

# ————— CONFIGURATION —————
REPO_DIR = '.'
FILE_NAME = 'uca_mv_filtered.ics'
URL_ICS = (
    "https://edt.uca.fr/jsp/custom/modules/plannings/"
    "anonymous_cal.jsp?resources=49414,49413,12012,27239,27238,26821&projectId=4&calType=ical&nbWeeks=8&displayConfigId=128"
)

# ————— TÉLÉCHARGEMENT —————
response = requests.get(URL_ICS)
response.raise_for_status()
cal = Calendar.from_ical(response.text)

# ————— NOUVEAU CALENDRIER —————
new_cal = Calendar()
new_cal.add('prodid', '-//UCA Filtered STPE MV M2 Calendar//')
new_cal.add('version', '2.0')

def has_token(text: str, token: str) -> bool:
    return re.search(rf"\b{re.escape(token)}\b", text) is not None

def accepte(desc, summary) -> bool:
    s = re.sub(r"\s+", " ", str(desc)).upper()
    title = re.sub(r"\s+", " ", str(summary)).upper()

    # Cas spécial : "VOLCAN" dans la description ou le titre → on affiche toujours
    if "VOLCAN" in s or "VOLCAN" in title:
        return True

    has_m1   = has_token(s, "M1")
    has_m2   = has_token(s, "M2")
    has_mv   = has_token(s, "MV")
    has_stpe = has_token(s, "STPE")
    has_scac = has_token(s, "SCAC")
    has_terre_primitive =
