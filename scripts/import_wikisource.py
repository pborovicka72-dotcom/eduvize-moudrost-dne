#!/usr/bin/env python3
"""Import historical proverb collection; fail loudly on empty discovery."""
import hashlib,json,pathlib,re,html,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
TITLE="Sbírka přísloví, pořekadel a průpovědí, kterých užívá náš lid rolnický"
def api(**params):
    url="https://cs.wikisource.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","formatversion":"2",**params})
    req=urllib.request.Request(url,headers={"User-Agent":"EduvizeWisdom/0.4 (https://github.com/pborovicka72-dotcom/eduvize-moudrost-dne)"})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def content(title):
    data=api(prop="revisions",titles=title,rvprop="content",rvslots="main")
    pages=data.get("query",{}).get("pages",[])
    revisions=pages[0].get("revisions",[]) if pages else []
    return revisions[0].get("slots",{}).get("main",{}).get("content","") if revisions else ""
def members():
    continuation={}
    while True:
        result=api(list="allpages",apprefix=TITLE+"/",apnamespace="0",aplimit="max",**continuation)
        yield from result.get("query",{}).get("allpages",[])
        if "continue" not in result:break
        continuation=result["continue"]
def lines(wikitext):
    for raw in wikitext.splitlines():
        s=raw.strip()
        if not s or s.startswith(("{{","}}","[[","|","<","=","__","{|","|-","!")):continue
        s=re.sub(r"^\*\s*","",s)
        if any(x in s for x in ("{{","}}","[[","<",">","|","http")):continue
        s=html.unescape(re.sub(r"'{2,5}","",s)).strip(" *#;:")
        if 25<=len(s)<=180 and re.search(r"[.!?]$",s):yield s
def main():
    parent=content(TITLE)
    if not parent:raise RuntimeError("Historical collection not found")
    if not re.search(r"PD[-_ ]old[-_ ]70",parent,re.I):
        raise RuntimeError("PD-old-70 work-level licence marker not found; refusing import")
    path=ROOT/"data/approved.json"
    existing=json.loads(path.read_text(encoding="utf-8"))
    seen={x["id"] for x in existing}
    inspected=added=0
    for page in members():
        title=page["title"]
        text=content(title)
        if not text:continue
        inspected+=1
        for quote in lines(text):
            uid=hashlib.sha256(("cs|"+title+"|"+quote).encode()).hexdigest()[:16]
            if uid in seen:continue
            existing.append({"id":uid,"text":quote,"language":"cs","topic":"Přísloví","author":"Lidové přísloví (sbírka Karel Hrubý, 1880)","work_title":TITLE,"source":"Wikizdroje","source_url":"https://cs.wikisource.org/wiki/"+urllib.parse.quote(title.replace(" ","_")),"rights":"PD-old-70","modified":False})
            seen.add(uid);added+=1
    if inspected==0:raise RuntimeError("Inspected 0 works: collection subpages not found")
    path.write_text(json.dumps(existing,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Inspected {inspected} works; imported {added} historical proverbs.")
if __name__=="__main__":main()
