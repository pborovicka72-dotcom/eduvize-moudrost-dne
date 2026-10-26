#!/usr/bin/env python3
"""Import clearly licensed short standalone works from Czech Wikisource.
Fail closed when licence or work boundaries are ambiguous."""
import hashlib,html,json,pathlib,re,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
API="https://cs.wikisource.org/w/api.php"
CATEGORIES=["Přísloví","Rčení","Aforismy"]
ALLOWED={
 "PD-traditional":("PD-traditional",None),
 "PD-old":("PD-old",None),
 "PD-old-70":("PD-old-70",None),
 "CC0":("CC0-1.0","https://creativecommons.org/publicdomain/zero/1.0/"),
 "CC0-1.0":("CC0-1.0","https://creativecommons.org/publicdomain/zero/1.0/"),
 "CC-by-4.0":("CC-BY-4.0","https://creativecommons.org/licenses/by/4.0/"),
 "CC-by-sa-4.0":("CC-BY-SA-4.0","https://creativecommons.org/licenses/by-sa/4.0/")
}
# Attribution-requiring licences need a verified author / rights-holder field.
ATTRIBUTION_REQUIRED={"CC-BY-4.0","CC-BY-SA-4.0"}
def api(params):
    url=API+"?"+urllib.parse.urlencode({"action":"query","format":"json","formatversion":"2",**params})
    req=urllib.request.Request(url,headers={"User-Agent":"EduvizeWisdom/0.3 (https://github.com/pborovicka72-dotcom/eduvize-moudrost-dne)"})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def licence(text):
    # Explicit work-level licence; site-wide footer is not evidence.
    names=re.findall(r"\\{\\{\\s*([^|{}\\n]+)",text)
    normalized=[re.sub(r"[_\\s]+","-",name.strip()).lower() for name in names]
    if any("nc" in name.split("-") or "nd" in name.split("-") or "copyright" in name or "copyvio" in name for name in normalized):
        return None
    found={key:entry for name in normalized for key,entry in ALLOWED.items() if name==key.lower()}
    # Ambiguous multiple licences require manual legal interpretation: skip.
    return next(iter(found.values())) if len(found)==1 else None
def author_from_metadata(text):
    # Never misrepresent the title of a page as the author.
    match=re.search(r"\\|\\s*(?:autor|author)\\s*=\\s*([^|{}\\n]+)",text,re.I)
    if not match:return None
    name=match.group(1).strip()
    return name if 2<=len(name)<=100 and not any(x in name for x in ("[","]","<",">")) else None
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
                license_info=licence(text)
                if not license_info:continue
                rights,license_url=license_info
                author=author_from_metadata(text)
                if rights in ATTRIBUTION_REQUIRED and not author:continue
                quote=extract(text)
                if not quote:continue
                uid=hashlib.sha256(("cs|"+title+"|"+quote).encode()).hexdigest()[:16]
                if uid in seen:continue
                existing.append({"id":uid,"text":quote,"language":"cs","topic":category,"author":author or "Autor neuveden","work_title":title,"source":"Wikizdroje","source_url":"https://cs.wikisource.org/wiki/"+urllib.parse.quote(title.replace(" ","_")),"rights":rights,"license_url":license_url,"modified":False})
                seen.add(uid);added+=1
            if "continue" not in response:break
            continuation=response["continue"]
    path.write_text(json.dumps(existing,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Inspected {inspected} works; imported {added} explicitly licensed, standalone short works.")
if __name__=="__main__":main()
