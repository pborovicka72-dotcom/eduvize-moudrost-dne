import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('carrier',Path(__file__).parents[1]/'scripts/apply_wisdom_actions_v2.py')
carrier=importlib.util.module_from_spec(spec)
spec.loader.exec_module(carrier)

class CarrierTests(unittest.TestCase):
    def test_preserve_current_pins_and_environment(self):
        old='<script src="/_environment.js"></script><script src="assets/wisdom.js?v=current"></script><div><a class="edu-admin__button" id="openOutput" href="signage.html">Otevřít</a><button id="copyOutput">Kopírovat</button></div>window.dispatchEvent(new Event("eduvize-profile-adapter-ready"));'
        result=carrier.html(old)
        self.assertIn('/_environment.js',result)
        self.assertEqual(result.count('id="generateOutput"'),1)
        self.assertEqual(result.count('output-controls.js'),1)
        self.assertIn('assets/wisdom.js?v=20261108-wisdom-actions-v2',result)
        self.assertIn('type="button" data-edu-open-output',result)
        with self.assertRaises(ValueError):carrier.html(result)
        with self.assertRaises(ValueError):carrier.html('Publikace'+old)
    def test_missing_carrier_fails_closed(self):
        with self.assertRaises(ValueError):carrier.html('<main>unknown</main>')
        with self.assertRaises(ValueError):carrier.legacy('unknown')

if __name__=='__main__':unittest.main()
