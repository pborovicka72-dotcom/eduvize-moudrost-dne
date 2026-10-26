#!/usr/bin/env python3
"""Import clearly licensed short standalone works from Czech Wikisource.
Fail closed when licence or work boundaries are ambiguous."""
import hashlib,html,json,pathlib,re,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
API="https://cs.wikisource.org/w/api.php"
CATEGORIES=["Přísloví","Rčení","Aforismy"]
ALLOWED={"PD-traditional":"PD-traditional","PD-old":"PD-old","PD-70":"PD-70","CC0":"CC0-1.0","CC-BY-4.0":"CC-BY-4.0","CC-BY-SA-4.0":"CC-BY-SA-4.0"}
def api(params):
    url=API+"?"+urllib.parse.urlencode({"action":"query","format":"json","formatversion":"2",**params})
    req=urllib.request.Request(url,headers={"User-Agent":"EduvizeWisdom/0.3 (https://github.com/pborovicka72-dotcom/eduvize-moudrost-dne)"})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def licence(text):
    # Only explicitly tagged work licences. Do not infer from site-wide CC BY-SA.
    tags=re.findall(r"\{\{\s*((?:PD[- ][\w-]+)|(?:CC[- ][\w. -]+))\s*(?:\||\}\})",text,re.I)
    for tag in tags:
        normalized=re.sub(r"\s+","-",tag.strip()).upper()
        for key,value in ALLOWED.items():
            if normalized==key.upper():return value
    return None
def extract(text):
    # Strict: one short, unformatted text line, not editorial commentary or a fragment of a longer work.
    text=re.sub(r"<ref\b[^>]*>.*?</ref>","",text,flags=re.I|re.S)
    lines=[x.strip() for x in text.splitlines() if x.strip() and not x.lstrip().startswith(("{{","[[Kategorie:","__"))]
    if len(lines)!=1:return None
    line=lines[0]
    if any(x in line for x in ("{{","[[","<","==","|","http")):return None
    value=html.unescape(re.sub(r"'{2,5}","",line)).strip(" *#;:")
    if not 25<=len(value)<=220:return None
    return value
def main():
    path=ROOT/"data/approved.json"
    existing=json.loads(path.read_text(encoding="utf-8"))
    seen={q["id"] for q in existing}
    added=0;inspected=0
    for category in CATEGORIES:
        continuation={}
        for _ in range(5):
            response=api({"list":"categorymembers","cmtitle":"Kategorie:"+category,"cmtype":"page","cmlimit":"50",**continuation})
            members=response.get("query",{}).get("categorymembers",[])
            for member in members:
                title=member["title"]
                data=api({"prop":"revisions","titles":title,"rvprop":"content","rvslots":"main"})
                pages=data.get("query",{}).get("pages",[])
                revisions=pages[0].get("revisions",[]) if pages else []
                if not revisions:continue
                text=revisions[0].get("slots",{}).get("main",{}).get("content","")
                inspected+=1
                rights=licence(text)
                if not rights:continue
                quote=extract(text)
                if not quote:continue
                uid=hashlib.sha256(("cs|"+title+"|"+quote).encode()).hexdigest()[:16]
                if uid in seen:continue
                existing.append({"id":uid,"text":quote,"language":"cs","topic":category,"author":title,"source":"Wikizdroje","source_url":"https://cs.wikisource.org/wiki/"+urllib.parse.quote(title.replace(" ","_")),"rights":rights})
                seen.add(uid);added+=1
            if "continue" not in response:break
            continuation=response["continue"]
    path.write_text(json.dumps(existing,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Inspected {inspected} works; imported {added} explicitly licensed, standalone short works.")
if __name__=="__main__":main()
