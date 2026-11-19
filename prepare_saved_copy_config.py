"""Narrow owner HTML patch; current input hash must be supplied by the sole TEST executor."""
import argparse
import hashlib
import json
from pathlib import Path


def once(source, before, after):
    if source.count(before) != 1:
        raise ValueError('Changed Wisdom source carrier; no fuzzy matching')
    return source.replace(before, after, 1)


def prepare(source):
    source=once(source,'<button class="edu-admin__button" id="generateOutput" type="button">Vygenerovat odkaz</button>','')
    source=once(source,'>Otevřít výstup</button>','>Otevřít náhled</button>')
    source=once(source,'</head>','<style data-wisdom-saved-workflow>#saveLocal{display:none!important}</style></head>')
    return source


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--before-sha256',required=True)
    parser.add_argument('--expected-after-sha256')
    parser.add_argument('--output',type=Path,help='Separate new staged candidate only; never overwrite the input')
    args=parser.parse_args();raw=args.input.read_bytes()
    digest=lambda b:hashlib.sha256(b).hexdigest()
    if digest(raw)!=args.before_sha256:raise ValueError('Current input CAS mismatch')
    after=prepare(raw.decode()).encode()
    if args.output:
        if digest(after)!=args.expected_after_sha256:raise ValueError('Reviewed after pin required')
        if args.input.read_bytes()!=raw:raise ValueError('Input changed during preparation')
        if args.output.resolve()==args.input.resolve():raise ValueError('Separate candidate path required')
        with args.output.open('xb') as stream:stream.write(after)
        args.output.chmod(0o644)
    print(json.dumps({'before':digest(raw),'after':digest(after),'beforeBytes':len(raw),'afterBytes':len(after),'candidateWritten':bool(args.output)}))
