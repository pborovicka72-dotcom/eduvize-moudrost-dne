import copy
import json
import sqlite3
import tempfile
import unittest
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from eduvize_admin.output_registry import OutputRegistry, Actor, OutputError
from eduvize_admin.output_api import router
from eduvize_wisdom.output_adapter import validate, get_output_adapters

PAYLOAD=dict(audience='all',dailyCount=2,authorRepeat='avoid',topics=[],authors=[],showSourceLink=False)
class Connection:
    def __init__(self,path):
        self.conn=sqlite3.connect(path,timeout=15);self.conn.execute('BEGIN IMMEDIATE')
    def execute(self,sql,args=()):
        if 'pg_advisory_xact_lock' in sql or sql == "SET LOCAL lock_timeout = '15s'":return self.conn.execute('SELECT 1')
        return self.conn.execute(sql.replace('%s','?'),args)
    def __enter__(self):return self
    def __exit__(self,typ,value,tb):
        self.conn.rollback() if typ else self.conn.commit();self.conn.close()

class WisdomOutputs(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=str(Path(self.tmp.name)/'test.db')
        self.connect=lambda:Connection(self.path)
        self.profiles={'b'*32:'a'*32,'d'*32:'c'*32};self.color='#112233';self.allowed=True
        self.actors={k:Actor(s,k,frozenset(['read','create','save','publish','revoke'])) for k,s in [('a','a'*32),('c','c'*32)]}
        def entitlement(school,app):
            if not self.allowed:raise OutputError(403,'FORBIDDEN','Test entitlement removed')
        self.entitlement=entitlement
        self.registry=self.new_registry()
        def auth(header):
            actor=self.actors.get(header.removeprefix('Bearer ') if header else '')
            if not actor:raise HTTPException(401)
            return actor
        app=FastAPI();app.include_router(router(self.registry,auth));self.client=TestClient(app)
        self.draft={'schemaVersion':1,'payloadVersion':1,'payload':PAYLOAD.copy(),'presentation':{'mode':'web','geometry':None,'interaction':'display'}}
        a=self.call('POST','/api/v1/output-assemblies',{'schemaVersion':1,'appId':'wisdom','profileId':'b'*32}).json()
        self.body={'schemaVersion':1,'appId':'wisdom','profileId':'b'*32,'assemblyId':a['id'],'draft':self.draft}
    def new_registry(self):
        return OutputRegistry(self.connect,get_output_adapters(),self.profiles.get,'https://test.skola.eduvize.cz',lambda p:self.theme(),self.entitlement)
    def theme(self):
        return dict(schemaVersion=1,colors={k:self.color for k in ['background','text','muted','surface','primary','primaryText','secondary','secondaryText','accent','border']},controls={'heightPx':44,'radiusPx':8},cards={'radiusPx':8},icons={'radiusPx':8})
    def call(self,method,path,body=None,key=None,actor='a'):
        return self.client.request(method,path,json=body,headers={'Authorization':'Bearer '+actor,'Idempotency-Key':key or str(uuid.uuid4())})
    def create(self):
        r=self.call('POST','/api/v1/outputs',self.body);self.assertEqual(r.status_code,201,r.text);return r.json()
    def publish(self,o):
        r=self.call('POST','/api/v1/outputs/'+o['id']+'/publish',{'expectedRevision':o['revision']});self.assertEqual(r.status_code,200,r.text);return r.json()
    def tearDown(self):self.tmp.cleanup()
    def test_strict_and_selected_catalog(self):
        for delta in [{'dailyCount':True},{'dailyCount':4},{'profileId':'d'*32},{'token':'secret'},{'topics':['unknown']},{'authors':['unknown']},{'showSourceLink':'1'},{'topics':['Humor','Humor']}]:
            with self.assertRaises(ValueError):validate({**PAYLOAD,**delta},{})
        self.assertEqual(validate(PAYLOAD,{}),PAYLOAD)
    def test_publication_is_immutable_and_profile_theme_is_scoped(self):
        o=self.publish(self.create());id=o['id'];path='/api/public/v1/outputs/'+id
        public=self.client.get(path);self.assertEqual(public.status_code,200,public.text)
        payload=public.json()['payload'];self.assertGreater(len(payload['quotes']),100)
        self.assertEqual(payload['settings'],PAYLOAD)
        self.assertEqual(len(payload['catalogSHA256']),64)
        for key in ['schoolId','profileId','assemblyId','token','connectionId']:
            self.assertNotIn(key,public.text)
        d=copy.deepcopy(self.draft);d['payload']['authors']=[payload['quotes'][0]['author']]
        saved=self.call('PUT','/api/v1/outputs/'+id+'/draft',{'expectedRevision':o['revision'],'draft':d}).json()
        self.assertEqual(self.client.get(path).json()['payload'],payload)
        updated=self.publish(saved);self.assertEqual(updated['url'],o['url'])
        newer=self.client.get(path).json()['payload'];self.assertEqual({q['author'] for q in newer['quotes']},{d['payload']['authors'][0]})
        self.color='#abcdef';self.assertEqual(self.client.get(path+'/theme').json()['colors']['primary'],'#abcdef')
        self.assertEqual(self.client.get('/o/'+id,follow_redirects=False).headers['location'],'/eduvize-moudrost-dne/published.html?edu-output='+id)
        self.assertEqual(self.call('GET','/api/v1/outputs/'+id,actor='c').status_code,404)
        self.assertEqual(self.new_registry().public(id)['payload'],newer)
        self.allowed=False;self.assertEqual(self.client.get(path).status_code,403)
        self.allowed=True;self.call('POST','/api/v1/outputs/'+id+'/revoke',{'expectedRevision':updated['revision']})
        self.assertEqual(self.client.get(path).status_code,410)
    def test_empty_filter_and_bad_draft_keep_previous_publication(self):
        o=self.publish(self.create());id=o['id'];before=self.client.get('/api/public/v1/outputs/'+id).json()
        d=copy.deepcopy(self.draft);d['payload']['authors']=['not in approved catalog']
        self.assertEqual(self.call('PUT','/api/v1/outputs/'+id+'/draft',{'expectedRevision':o['revision'],'draft':d}).status_code,422)
        self.assertEqual(self.client.get('/api/public/v1/outputs/'+id).json(),before)

if __name__=='__main__':unittest.main()
