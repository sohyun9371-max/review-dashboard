"""Conservative campaign checks. Never infer driving time from a city name."""
import json,re,time
from pathlib import Path
from datetime import datetime,timezone,timedelta
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).parent
KST=timezone(timedelta(hours=9))
TODAY=datetime.now(KST).date()
ALLOW=("수원","영통","광교","동탄","용인","기흥","화성","오산","군포","의왕","안양","과천","성남","분당","판교")
BLOCK=("체험단 공고 통계","모집현황","공지사항")
WEEKEND_YES=re.compile(r"(주말.{0,12}(가능|방문|체험|운영)|토[·, /~및과]+일.{0,10}(가능|방문|체험)|토요일.{0,15}(가능|방문|체험)|일요일.{0,15}(가능|방문|체험))")
WEEKEND_NO=re.compile(r"(주말.{0,12}(불가|제외|휴무)|토[·, /~및과]+일.{0,12}(불가|제외|휴무))")
DEADLINE=re.compile(r"(?:신청|모집|지원).{0,12}(?:마감|기간|종료).{0,25}?(20\d{2})[./-](\d{1,2})[./-](\\d{1,2})")
session=requests.Session()
session.headers.update({"User-Agent":"Mozilla/5.0 (compatible; CampaignStatusChecker/1.0)"})
items=json.loads((ROOT/"candidates.json").read_text(encoding="utf-8"))
clean=[]
for item in items:
    title=item.get("title","")
    url=item.get("url","")
    if not url.startswith("https://") or any(x in title for x in BLOCK):
        continue
    if not any(x in title+" "+item.get("location","") for x in ALLOW):
        continue
    if urlparse(url).netloc=="moaalarm.boheapps.com" and "/campaigns/" not in urlparse(url).path:
        continue
    clean.append(item)
print(f"Geographic candidates: {len(clean)} / {len(items)}",flush=True)
for i,item in enumerate(clean):
    item["weekend_status"]="unknown"
    item["recruitment_status"]="unknown"
    item["drive_minutes"]=None
    item["verification_note"]="원문에서 주말 방문·모집기간·차량 이동시간 확인 필요"
    try:
        resp=session.get(item["url"],timeout=8)
        resp.raise_for_status()
        soup=BeautifulSoup(resp.text,"html.parser")
        for x in soup(["script","style","nav","footer"]):x.decompose()
        body=soup.get_text(" ",strip=True)[:20000]
        if WEEKEND_NO.search(body):
            item["weekend_status"]="no"
        elif WEEKEND_YES.search(body):
            item["weekend_status"]="possible"
        m=DEADLINE.search(body)
        if m:
            try:
                date=datetime(int(m[1]),int(m[2]),int(m[3])).date()
                item["recruitment_status"]="expired" if date<TODAY else "possible"
                item["deadline"]=date.isoformat()
            except ValueError:pass
        item["verification_note"]="원문 자동 확인(요일·마감일 추출은 참고용). 정확한 방문주소 및 실시간 차량 이동시간 미검증"
    except requests.RequestException as e:
        item["verification_note"]="원문 접속 실패: "+str(e)[:100]
    if (i+1)%30==0:print(f"Checked {i+1}/{len(clean)}",flush=True)
(ROOT/"candidates.json").write_text(json.dumps(clean,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
# Do not label anything fully verified without an exact address and routing result.
(ROOT/"campaigns.json").write_text("[]\n",encoding="utf-8")
print(f"Saved {len(clean)} regional candidates; weekend possible: {sum(x['weekend_status']=='possible' for x in clean)}; fully verified: 0",flush=True)
