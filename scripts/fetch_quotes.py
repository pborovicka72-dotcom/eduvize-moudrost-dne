#!/usr/bin/env python3
"""Fetch ZenQuotes, translate with DeepL, and queue candidates for human approval."""
import json, os, pathlib, urllib.request, urllib.error, hashlib, datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
PENDING=ROOT/"data"/"pending.json"
APPROVED=ROOT/"data"/"approved.json"
def read(path):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:return []
def request(url,headers=None,payload=None):
    req=urllib.request.Request(url,data=payload,headers=headers or {"User-Agent":"Eduvize-Wisdom/1.0"})
    with urllib.request.urlopen(req,timeout=25) as r:return json.load(r)
def translate(text,lang,key):
    base="https://api-free.deepl.com" if key.endswith(":fx") else "https://api.deepl.com"
    data=json.dumps({"text":[text],"source_lang":"EN","target_lang":lang}).encode()
    res=request(base+"/v2/translate",{"Authorization":"DeepL-Auth-Key "+key,"Content-Type":"application/json"},data)
    return res["translations"][0]["text"]
def main():
    key=os.getenv("DEEPL_API_KEY")
    if not key:raise SystemExit("DEEPL_API_KEY secret is missing")
    # ZenQuotes free API has no guaranteed keyword/tag filtering.
    raw=request("https://zenquotes.io/api/quotes")
    pending=read(PENDING);approved=read(APPROVED)
    seen={x["id"] for x in pending+approved}
    added=0
    for item in raw:
        en=(item.get("q") or "").strip();author=(item.get("a") or "").strip()
        if not en or len(en)>240 or not author or en.lower().startswith("too many requests"):continue
        uid=hashlib.sha256((en+"|"+author).encode()).hexdigest()[:16]
        if uid in seen:continue
        # New quotes are NEVER published automatically. A moderator must approve them.
        try:
            cs=translate(en,"CS",key);sk=translate(en,"SK",key)
        except (urllib.error.HTTPError,urllib.error.URLError,KeyError) as e:
            print("Translation failed:",e);break
        pending.append({"id":uid,"en":en,"cs":cs,"sk":sk,"author":author,"source":"ZenQuotes","status":"pending","added_at":datetime.datetime.now(datetime.timezone.utc).isoformat()})
        seen.add(uid);added+=1
        if added>=10:break
    PENDING.parent.mkdir(parents=True,exist_ok=True)
    PENDING.write_text(json.dumps(pending,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("New candidates:",added)
if __name__=="__main__":main()
