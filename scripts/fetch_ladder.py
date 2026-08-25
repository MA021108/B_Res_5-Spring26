import requests, json, re, datetime
from bs4 import BeautifulSoup

URL = "https://www.nsnta.org/v2/ladders.php?comp=mens&season=2026S"
GRADE_ID = "g-b-reserve-5"
TEAM = "Greenvale"

resp = requests.get(URL, timeout=20, headers={"User-Agent": "Mozilla/5.0 (ladder-sync-bot)"})
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

anchor = soup.find(id=GRADE_ID)
if anchor is None:
    raise SystemExit(f"Could not find section with id={GRADE_ID} - site structure may have changed")

table = anchor.find_next("table")
if table is None:
    raise SystemExit("Could not find a table after the grade anchor")

rows = []
for tr in table.find_all("tr")[1:]:
    cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
    if len(cells) < 6:
        continue
    pos, team, pts, w, l, pct = cells[:6]
    try:
        rows.append({
            "pos": int(pos), "team": team,
            "pts": int(pts), "w": int(w), "l": int(l), "pct": int(pct)
        })
    except ValueError:
        continue

if not rows:
    raise SystemExit("Parsed zero rows - aborting so we don't overwrite good data with nothing")

caption_match = soup.find(string=re.compile(r"after Round \d+"))
caption = caption_match.strip() if caption_match else None

data = {
    "grade": "B-5",
    "team": TEAM,
    "rows": rows,
    "caption": caption,
    "updated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
}

with open("ladder.json", "w") as f:
    json.dump(data, f, indent=2)

print(json.dumps(data, indent=2))
