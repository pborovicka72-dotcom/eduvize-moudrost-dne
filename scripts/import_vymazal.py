#!/usr/bin/env python3
"""Candidate extraction from František Vymazal's 1911 public-domain book.
Never publishes candidates directly to approved.json: editorial safety gate.
"""
import json,re,html,pathlib,urllib.request,urllib.parse
ROOT=pathlib.Path(__file__).resolve().parents[1]
TITLE="Tisíc nových zrnek"
URL="https://cs.wikisource.org/wiki/Tis%C3%ADc_nov%C3%BDch_zrnek"
def main():
    params=urllib.parse.urlencode({"action":"query","format":"json","formatversion":"2","prop":"revisions","titles":TITLE,"rvprop":"content","rvslots":"main"})
    req=urllib.request.Request("https://cs.wikisource.org/w/api.php?"+params,headers={"User-Agent":"EduvizeWisdom/0.5 (https://github.com/pborovicka72-dotcom/eduvize-moudrost-dne)"})
    with urllib.request.urlopen(req,timeout=45) as r:data=json.load(r)
    pages=data.get("query",{}).get("pages",[])
    rev=pages[0].get("revisions",[]) if pages else []
    if not rev:raise RuntimeError("Wikisource book not found")
    raw=rev[0]["slots"]["main"]["content"]
    if not re.search(r"PD[-_ ]old[-_ ]70",raw,re.I):
        raise RuntimeError("No verified work-level PD-old-70 marker")
    # The work includes racist, sectarian and outdated political remarks.
    # Import is candidates-only until human-readable screening, never unattended publication.
    candidates=[]
    for match in re.finditer(r"(?m)^\s*(\d{1,4})\.\s+(.+?)(?=\n\s*\d{1,4}\.\s|\Z)",raw,re.S):
        number=int(match.group(1));s=match.group(2).strip().splitlines()[0].strip()
        if any(t in s for t in ("{{","[[","<",">","|","http")):continue
        s=html.unescape(re.sub(r"'{2,5}","",s))
        if not 35<=len(s)<=180:continue
        candidates.append({"id":f"vymazal-{number:04d}","text":s,"language":"cs","topic":"Moudrost","author":"František Vymazal (sběratel; původní autor výroku nemusí být znám)","source":"Tisíc nových zrnek (1911)","source_url":URL,"rights":"PD-old-70","review_status":"candidate"})
    if not candidates:raise RuntimeError("No numbered sayings extracted; inspect wikitext structure")
    path=ROOT/"data/candidates_vymazal.json"
    path.write_text(json.dumps(candidates,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Extracted {len(candidates)} candidates. Approved database intentionally unchanged.")
if __name__=="__main__":main()
