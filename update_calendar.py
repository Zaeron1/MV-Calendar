import os
import requests
from icalendar import Calendar, Event

# ————— CONFIGURATION —————
REPO_DIR = '.'
FILE_NAME = 'uca_mv_filtered.ics'
URL_ICS = (
    "https://edt.uca.fr/jsp/custom/modules/plannings/"
    "anonymous_cal.jsp?resources=17227,17226,15732,15724,"
    "10397,10385,10384,7652&projectId=3&calType=ical&nbWeeks=20&displayConfigId=128"
)

# ————— TÉLÉCHARGEMENT ET PARSING —————
response = requests.get(URL_ICS)
response.raise_for_status()

cal = Calendar.from_ical(response.text)
new_cal = Calendar()
new_cal.add('prodid', '-//UCA Filtered MV Calendar//mxm.dk//')
new_cal.add('version', '2.0')

# ————— FILTRAGE DES ÉVÉNEMENTS —————
for comp in cal.walk():
    if comp.name == "VEVENT":
        desc = comp.get('description', '')

        if (
            ("MV" in desc and "M2" not in desc)
            or ("STPE" in desc and "STPE ScAC" not in desc)
        ):
            new_cal.add_component(comp)

# ————— SAUVEGARDE —————
file_path = os.path.join(REPO_DIR, FILE_NAME)
with open(file_path, "wb") as f:
    f.write(new_cal.to_ical())

print(f"✅ '{FILE_NAME}' mis à jour.")
