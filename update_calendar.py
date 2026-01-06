import os
import requests
from icalendar import Calendar

# ————— CONFIGURATION —————
REPO_DIR = '.'
FILE_NAME = 'uca_mv_filtered.ics'
URL_ICS = (
    "https://edt.uca.fr/jsp/custom/modules/plannings/"
    "anonymous_cal.jsp?resources=17227,17226,15732,15724,"
    "10397,10385,10384,7652&projectId=3&calType=ical&nbWeeks=20&displayConfigId=128"
)

# ————— TÉLÉCHARGEMENT —————
response = requests.get(URL_ICS)
response.raise_for_status()

cal = Calendar.from_ical(response.text)

# ————— NOUVEAU CALENDRIER —————
new_cal = Calendar()
new_cal.add('prodid', '-//UCA Filtered STPE MV M1 Calendar//')
new_cal.add('version', '2.0')

# ————— FONCTION DE FILTRAGE —————
def accepte_evenement(desc: str) -> bool:
    desc = str(desc)

    # PRIORITÉ ABSOLUE : M1
    if "M1" in desc:
        return True

    # CAS MV (hors M2)
    if "MV" in desc and "M2" not in desc:
        return True

    # CAS STPE uniquement (hors M2 et ScAC)
    if (
        "STPE" in desc
        and "M2" not in desc
        and "ScAC" not in desc
    ):
        return True

    return False

# ————— FILTRAGE DES ÉVÉNEMENTS —————
for comp in cal.walk():
    if comp.name == "VEVENT":
        desc = comp.get('description', '')

        if accepte_evenement(desc):
            new_cal.add_component(comp)

# ————— SAUVEGARDE —————
file_path = os.path.join(REPO_DIR, FILE_NAME)
with open(file_path, "wb") as f:
    f.write(new_cal.to_ical())

print(f"✅ '{FILE_NAME}' mis à jour avec le filtre STPE / MV / M1.")
