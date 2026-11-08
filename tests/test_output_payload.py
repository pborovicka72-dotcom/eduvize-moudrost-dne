"""Portable adapter tests; real registry HTTP tests run in the core integration environment."""
import hashlib
import json
import unittest
from pathlib import Path
from eduvize_wisdom.output_adapter import catalog, prepare, validate

SETTINGS=dict(audience='all',dailyCount=2,authorRepeat='avoid',topics=[],authors=[],showSourceLink=False)

class PayloadTests(unittest.TestCase):
    def test_catalog_copy_matches_editor_catalog(self):
        rows,digest=catalog()
        self.assertGreater(len(rows),100)
        self.assertEqual(digest,hashlib.sha256((Path(__file__).parents[1]/'data/approved.json').read_bytes()).hexdigest())
    def test_closed_settings(self):
        for delta in [{'dailyCount':True},{'dailyCount':0},{'dailyCount':4},{'profileId':'x'},{'token':'x'},{'showSourceLink':'1'},{'topics':['unknown']},{'authors':['unknown']},{'topics':['Humor','Humor']}]:
            with self.assertRaises(ValueError):validate({**SETTINGS,**delta},None)
        self.assertEqual(validate(SETTINGS,None),SETTINGS)
    def test_prepare_filters_and_pins_only_public_quotes(self):
        rows,_=catalog();author=rows[0]['author']
        settings={**SETTINGS,'authors':[author],'audience':'primary'}
        public,media=prepare(None,settings,None)
        self.assertEqual(media,[]);self.assertEqual(public['settings'],settings)
        self.assertTrue(public['quotes'])
        self.assertEqual({q['author'] for q in public['quotes']},{author})
        self.assertNotIn('audience',public['quotes'][0])
        serialized=json.dumps(public)
        for private in ['profileId','schoolId','connectionId','access_token','assemblyId']:
            self.assertNotIn(private,serialized)
        settings['authors'].append('unknown')
        self.assertEqual(public['settings']['authors'],[author])

if __name__=='__main__':unittest.main()
