"""Offline source-carrier patch for the sole TEST builder; never edits a live tree itself."""
import argparse
from pathlib import Path
import re


def once(pattern, replacement, source):
    result, count = re.subn(pattern, lambda _: replacement, source)
    if count != 1:
        raise ValueError('Unexpected Wisdom source carrier; do not overwrite the file')
    return result


def html(source):
    if re.search(r'publication-admin|data-output-admin|Publikace', source):
        raise ValueError('Remove the existing technical publication controller atomically before integration')
    scripts = ''.join('<script src="'+path+'?v=20261108-wisdom-actions-v2"></script>' for path in [
        '/eduvize-styly/design-system/output-client.js',
        '/eduvize-styly/design-system/output-actions.js',
        'assets/load-saved-app.js', 'assets/output-adapter.js', 'assets/output-controls.js'])
    source = once(r'<script src="assets/wisdom\.js\?[^\"]+"></script>',
                  scripts+'<script src="assets/wisdom.js?v=20261108-wisdom-actions-v2"></script>', source)
    source = once(r'<a\b(?=[^>]*\bid="openOutput")[^>]*>[^<]*</a>',
                  '<button class="edu-admin__button" id="generateOutput" type="button">Vygenerovat odkaz</button>'
                  '<button class="edu-admin__button" id="openOutput" type="button" data-edu-open-output>Otevřít výstup</button>', source)
    pattern = r'(<button\b(?=[^>]*\bid="copyOutput")[^>]*>[^<]*</button></div>)'
    matches = list(re.finditer(pattern, source))
    if len(matches) != 1:
        raise ValueError('Unexpected Wisdom output controls')
    match = matches[0]
    source = source[:match.end()]+'<p id="outputStatus" class="edu-admin__hint" role="status" aria-live="polite"></p>'+source[match.end():]
    return once(re.escape('window.dispatchEvent(new Event("eduvize-profile-adapter-ready"));'),
                'window.EduvizeWisdomOutputControls.install(window.EduvizeProfileAdapter);\n'
                'window.dispatchEvent(new Event("eduvize-profile-adapter-ready"));', source)


def legacy(source):
    source = once(re.escape("$('openOutput').addEventListener('click',"),
                  "if(!window.EduvizeWisdomManagedOutput){$('openOutput').addEventListener('click',", source)
    return once(re.escape("for(const id of ['audience','dailyCount','authorRepeat','outputType','topics','authors','showSourceLink'])"),
                "}for(const id of ['audience','dailyCount','authorRepeat','outputType','topics','authors','showSourceLink'])", source)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_root', type=Path)
    parser.add_argument('--write', action='store_true', help='Write only the two offline staged source carriers')
    args = parser.parse_args()
    files = [('config.html', html), ('assets/wisdom.js', legacy)]
    # Compute BOTH changes first; an unknown carrier never partially patches files.
    updates = [(args.source_root/name, fn((args.source_root/name).read_text())) for name, fn in files]
    for path, text in updates:
        if args.write:
            path.write_text(text)
        print(('patched ' if args.write else 'checked ')+str(path))
