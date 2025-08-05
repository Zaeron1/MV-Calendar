import os
import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz

# ————— CONFIGURATION —————
REPO_DIR = '.'
FILE_NAME = 'uca_mv_filtered.ics'
URL_ICS = (
    "https://edt.uca.fr/jsp/custom/modules/plannings/"
    "anonymous_cal.jsp?resources=17227,17226,15732,15724,"
    "10397,10385,10384,7652&projectId=3&calType=ical&nbWeeks=20&displayConfigId=128"
)
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
        if "MV" in desc and ("M2" not in desc or "M1" in desc):
            new_cal.add_component(comp)

# ————— SUPPRESSION DU DERNIER ÉVÉNEMENT 'Dernière mise à jour' —————
update_events = [
    comp for comp in new_cal.walk()
    if comp.name == "VEVENT" and comp.get('summary') == "Dernière mise à jour du calendrier"
]
if update_events:
    latest_event = max(
        update_events,
        key=lambda ev: ev.get('dtstart').dt if ev.get('dtstart') else datetime.min
    )
    new_cal.subcomponents.remove(latest_event)

# ————— AJOUT DU NOUVEL ÉVÉNEMENT 'Dernière mise à jour' —————
now = datetime.now(pytz.timezone(TZ))
event = Event()
event.add('summary', 'Dernière mise à jour du calendrier')
event.add('dtstart', now)
event.add('dtend', now + timedelta(minutes=15))
event.add('dtstamp', now)
new_cal.add_component(event)

# ————— SAUVEGARDE —————
file_path = os.path.join(REPO_DIR, FILE_NAME)
with open(file_path, "wb") as f:
    f.write(new_cal.to_ical())

print(f"✅ '{FILE_NAME}' mis à jour.")
