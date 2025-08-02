import os
import subprocess
import requests
from icalendar import Calendar
from datetime import datetime
import pytz

# ————— CONFIGURATION —————

# Chemin vers votre dépôt Git local (doit déjà exister et avoir un remote "origin" configuré)
REPO_DIR = '/chemin/vers/votre/depot'

# Nom du fichier ICS dans le dépôt
FILE_NAME = 'uca_mv_filtered.ics'

# URL du calendrier UCA
URL_ICS = (
    "https://edt.uca.fr/jsp/custom/modules/plannings/"
    "anonymous_cal.jsp?resources=17227,17226,15732,15724,"
    "10397,10385,10384,7652&projectId=3&calType=ical&nbWeeks=20&displayConfigId=128"
)

# Fuseau horaire pour l'horodatage du commit
TZ = 'Europe/Brussels'

# ————— TÉLÉCHARGEMENT ET FILTRAGE —————

response = requests.get(URL_ICS)
response.raise_for_status()

cal = Calendar.from_ical(response.text)
new_cal = Calendar()
new_cal.add('prodid', '-//UCA Filtered MV Calendar//mxm.dk//')
new_cal.add('version', '2.0')

for comp in cal.walk():
    if comp.name == "VEVENT":
        desc = comp.get('description', '')
        if "MV" in desc and "M2" not in desc:
            new_cal.add_component(comp)

# ————— SAUVEGARDE DANS LE DÉPÔT —————

# Chemin absolu du fichier ICS dans votre dépôt
file_path = os.path.join(REPO_DIR, FILE_NAME)

# Écriture du fichier
with open(file_path, "wb") as f:
    f.write(new_cal.to_ical())

print(f"✅ '{FILE_NAME}' mis à jour dans le dépôt.")

# ————— COMMIT & PUSH —————

# On se place dans le dépôt
os.chdir(REPO_DIR)

# 1) git add
subprocess.run(["git", "add", FILE_NAME], check=True)

# 2) git commit
now = datetime.now(pytz.timezone(TZ))
commit_msg = f"Update ICS le {now.strftime('%Y-%m-%d %H:%M:%S')}"
# Si aucun changement à committer, on ignore
res = subprocess.run(
    ["git", "diff", "--cached", "--quiet"]
)
if res.returncode != 0:
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    print(f"📝 Commit: {commit_msg}")
else:
    print("ℹ️  Pas de changements à committer.")

# 3) git push
subprocess.run(["git", "push"], check=True)
print("🚀 Push vers GitHub effectué.")