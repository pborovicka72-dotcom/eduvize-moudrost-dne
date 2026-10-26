#!/usr/bin/env python3
"""Import candidates from cs/sk Wikiquote categories. No automatic publication."""
import hashlib, html, json, pathlib, re, urllib.parse, urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
CATEGORIES=json.loads((ROOT/"data/categories.json").read_text(encoding="utf-8"))
def load(name):
    return json.loads((ROOT/"data"/name).read_text(encoding="utf-8"))
def api(lang,params):
    params={"action":"query","format":"json","formatversion":"2",**params}
    url="https://"+lang+".wikiquote.org/w/api.php?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={"User-Agent":"EduvizeWisdom/0.1 (educational kiosk; contact via GitHub pborovicka72-dotcom/eduvize-moudrost-dne)"})
    with urllib.request.urlopen(req,timeout=30) as response:return json.load(response)
def strip_markup(text):
    text=re.sub(r"<ref\b[^>]*>.*?</ref>|<ref\b[^>]*/>","",text,flags=re.I|re.S)
    text=re.sub(r"\{\{[^{}]*\}\}","",text)
    text=re.sub(r"\[\[(?:[^]|]*\|)?([^]]+)\]\]",r"\1",text)
    text=re.sub(r"\[https?://[^ ]+\s+([^]]+)\]",r"\1",text)
    text=re.sub(r"<[^>]+>","",text)
    return html.unescape(re.sub(r"'{2,5}","",text)).strip(" •*#;:–—\t ")
def candidates(wikitext):
    for line in wikitext.splitlines():
        if not re.match(r"^\*\s+[^*#]",line):continue
        line=re.sub(r"^\*\s+","",line)
        if "{{" in line or "{|" in line:continue
        value=strip_markup(line)
        if 35<=len(value)<=240 and not re.search(r"\b(?:https?://|ISBN|Kategorie:)\b",value,re.I):
            yield value
def main():
    pending=load("pending.json");approved=load("approved.json")
    seen={x.get("id") for x in pending+approved}
    count=0
    for lang in ("cs","sk"):
        for category in CATEGORIES.get(lang,[]):
            data=api(lang,{"list":"categorymembers","cmtitle":"Kategorie:"+category,"cmtype":"page","cmlimit":"20"})
            pages=data.get("query",{}).get("categorymembers",[])
            for page in pages[:10]:
                title=page["title"]
                content=api(lang,{"prop":"revisions","titles":title,"rvprop":"content","rvslots":"main"})
                entries=content.get("query",{}).get("pages",[])
                if not entries:continue
                rev=entries[0].get("revisions",[])
                if not rev:continue
                wiki=rev[0].get("slots",{}).get("main",{}).get("content","")
                for quote in list(candidates(wiki))[:5]:
                    uid=hashlib.sha256((lang+"|"+title+"|"+quote).encode()).hexdigest()[:16]
                    if uid in seen:continue
                    pending.append({"id":uid,"text":quote,"language":lang,"topic":category,"author":title,"source":"Wikicitáty","source_url":"https://"+lang+".wikiquote.org/wiki/"+urllib.parse.quote(title.replace(" ","_")),"status":"pending"})
                    seen.add(uid);count+=1
                    if count>=60:break
                if count>=60:break
            if count>=60:break
        if count>=60:break
    (ROOT/"data/pending.json").write_text(json.dumps(pending,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Queued",count,"candidates. Review before publication.")
if __name__=="__main__":main()
