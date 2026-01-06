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

    has_stpe = "STPE" in desc
    has_mv   = "MV" in desc
    has_m1   = "M1" in desc
    has_m2   = "M2" in desc
    has_scac = "ScAC" in desc

    # 1) Doit concerner STPE ou MV
    if not (has_stpe or has_mv):
        return False

    # 2) ScAC bloque seulement si MV n’est PAS présent
    if has_scac and not has_mv:
        return False

    # 3) Si M1 est présent → OK
    if has_m1:
        return True

    # 4) Sinon, M2-only → rejet
    if has_m2:
        return False

    # 5) Cas STPE/MV sans mention de niveau → OK
    return True

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
