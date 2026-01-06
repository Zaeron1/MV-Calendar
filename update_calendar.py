import os
import re
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

def has_token(text: str, token: str) -> bool:
    # match "token" comme mot entier (ex: M1, M2, MV, STPE, ScAC)
    return re.search(rf"\b{re.escape(token)}\b", text) is not None

def accepte(desc) -> bool:
    s = re.sub(r"\s+", " ", str(desc)).upper()

    has_m1   = has_token(s, "M1")
    has_m2   = has_token(s, "M2")
    has_mv   = has_token(s, "MV")
    has_stpe = has_token(s, "STPE")
    has_scac = has_token(s, "SCAC")  # on met tout en upper

    level_ok = has_m1 or (not has_m2)

    # 1) MV : on accepte (M1) ou (pas M2) — ScAC n'empêche pas si MV est là
    if has_mv and level_ok:
        return True

    # 2) Sinon, STPE seul : on rejette ScAC, et on rejette M2-only
    if (not has_mv) and has_stpe and (not has_scac) and level_ok:
        return True

    return False

# ————— FILTRAGE —————
for comp in cal.walk():
    if comp.name == "VEVENT":
        desc = comp.get('description', '')
        if accepte(desc):
            new_cal.add_component(comp)

# ————— SAUVEGARDE —————
file_path = os.path.join(REPO_DIR, FILE_NAME)
with open(file_path, "wb") as f:
    f.write(new_cal.to_ical())

print(f"✅ '{FILE_NAME}' mis à jour.")

