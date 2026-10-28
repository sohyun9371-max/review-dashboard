"""Public listing best-effort importer. Never labels weekend/drive-time as verified."""
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE="https://moaalarm.boheapps.com"
OUT=Path(__file__).with_name("candidates.json")
KST=timezone(timedelta(hours=9))
REGIONS=("수원","영통","광교","동탄","용인","기흥","화성","오산","군포","의왕","안양","과천","성남","분당","판교","광명","시흥","안산","평택","서울")
HEADERS={"User-Agent":"WeekendCampaignDashboard/0.1 (+public listing research)"}

def collect():
    items=[]
    session=requests.Session()
    for delta in range(7):
        day=(datetime.now(KST)-timedelta(days=delta)).strftime("%Y-%m-%d")
        url=f"{BASE}/campaigns/{day}/"
        try:
            response=session.get(url,headers=HEADERS,timeout=18)
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"Skip {url}: {exc}")
            continue
        soup=BeautifulSoup(response.text,"html.parser")
        print(f"Loaded {url}: {response.status_code}, {len(response.content)} bytes")
        # A listing link must have an explicit campaign path; do not guess from headings.
        links=soup.select('a[href]')
        print(f"Found {len(links)} links on {url}")
        for a in links:
            href=urljoin(url,a.get("href",""))
            if not href.startswith(BASE+"/") or not re.search(r"/campaigns/[^/]+/.+",href):
                continue
            parent=a.find_parent(["article","li"]) or a.parent
            if parent is None:
                continue
            snippet=parent.get_text(" ",strip=True)
            if not any(place in snippet for place in REGIONS):
                continue
            if "방문형" not in snippet or "블로그" not in snippet:
                continue
            title=a.get_text(" ",strip=True) or snippet[:85]
            if len(title)<5:
                continue
            items.append({"title":title[:160],"source":"모아알림","location":next((r for r in REGIONS if r in snippet),"지역 확인 필요"),"url":href,"weekend_status":"unknown","drive_minutes":None})
    unique={x["url"]:x for x in items}
    return list(unique.values())

if __name__=="__main__":
    data=collect()
    if data:
        OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Candidates: {len(data)}; existing data preserved on empty result")
