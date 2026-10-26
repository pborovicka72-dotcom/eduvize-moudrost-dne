#!/usr/bin/env python3
"""Automated, conservative Wikiquote publishing. Unverified rights => skip."""
import hashlib, html, json, pathlib, re, urllib.parse, urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
CATEGORIES=json.loads((ROOT/"data/categories.json").read_text(encoding="utf-8"))
def api(lang,params):
    url="https://"+lang+".wikiquote.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","formatversion":"2",**params})
    req=urllib.request.Request(url,headers={"User-Agent":"EduvizeWisdom/0.2 (https://github.com/pborovicka72-dotcom/eduvize-moudrost-dne)"})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def clean(s):
    s=re.sub(r"<ref\b[^>]*>.*?</ref>|<ref\b[^>]*/>","",s,flags=re.I|re.S)
    s=re.sub(r"\[\[(?:[^]|]*\|)?([^]]+)\]\]",r"\1",s)
    s=re.sub(r"<[^>]+>","",s)
    return html.unescape(re.sub(r"'{2,5}","",s)).strip(" •*#;:–—\t ")
def extract(wikitext):
    for line in wikitext.splitlines():
        if not re.match(r"^\*\s+[^*#]",line):continue
        line=re.sub(r"^\*\s+","",line)
        if "{{" in line or "{|" in line:continue
        value=clean(line)
        if 35<=len(value)<=220 and not re.search(r"https?://|ISBN|Kategorie:",value,re.I):yield value
def rights_verified(page,quote):
    """Fail closed. Category membership, page licence and author age are NOT proof.
    A future reliable per-quotation rights verification may be added here."""
    return False
def main():
    approved=json.loads((ROOT/"data/approved.json").read_text(encoding="utf-8"))
    seen={x.get("id") for x in approved}
    checked=0;published=0
    for lang in ("cs","sk"):
        for category in CATEGORIES.get(lang,[]):
            data=api(lang,{"list":"categorymembers","cmtitle":"Kategorie:"+category,"cmtype":"page","cmlimit":"20"})
            for page in data.get("query",{}).get("categorymembers",[])[:10]:
                title=page["title"]
                data=api(lang,{"prop":"revisions","titles":title,"rvprop":"content","rvslots":"main"})
                pages=data.get("query",{}).get("pages",[])
                rev=pages[0].get("revisions",[]) if pages else []
                if not rev:continue
                wikitext=rev[0].get("slots",{}).get("main",{}).get("content","")
                for quote in list(extract(wikitext))[:5]:
                    checked+=1
                    if not rights_verified(page,quote):continue
                    uid=hashlib.sha256((lang+"|"+title+"|"+quote).encode()).hexdigest()[:16]
                    if uid in seen:continue
                    approved.append({"id":uid,"text":quote,"language":lang,"topic":category,"author":title,"source":"Wikicitáty","source_url":"https://"+lang+".wikiquote.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))})
                    seen.add(uid);published+=1
    (ROOT/"data/approved.json").write_text(json.dumps(approved,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Checked {checked} candidate quotes; automatically published {published}. Unverified rights are excluded.")
if __name__=="__main__":main()
