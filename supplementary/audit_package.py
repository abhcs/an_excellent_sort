"""Check package bindings; this does not run a SAT solver or DRAT checker."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent

def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()

def verify(entry):
    path = HERE / entry['path']
    assert path.is_file(), str(path)
    assert digest(path) == entry['sha256'], entry['path']
    if 'bytes' in entry:
        assert path.stat().st_size == entry['bytes'], entry['path']

manifest = json.loads((HERE / 'source-manifest.json').read_text())
ledger = json.loads((HERE / 'claim-ledger.json').read_text())
assert digest(HERE / 'source-manifest.json') == ledger['source_manifest_sha256']
for entry in manifest['files']:
    verify(entry)
for claim in ledger['claims']:
    for entry in claim['evidence']:
        verify(entry)
for case in ledger['whole_case_certificates']:
    for entry in case['files'].values():
        verify(entry)
historical = json.loads((HERE / 'research/d18-search/results/structural-cover-progress-round2.json').read_text())
by_case = {c['case_id']: c for c in historical['certificates']}
keys = {'result': 'result_sha256', 'cnf': 'cnf_sha256', 'proof': 'proof_sha256', 'checker_log': 'checker_log_sha256'}
for case in ledger['whole_case_certificates']:
    for role, key in keys.items():
        assert case['files'][role]['sha256'] == by_case[case['case_id']][key]
for width, entry in ledger['cover_hashes'].items():
    assert digest(HERE / f'research/d18-search/prefixes/complete{width}.jsonl') == entry['cover_sha256']
assert len(ledger['whole_case_certificates']) == 7
result = dict(status='PASS', frozen_source_files=len(manifest['files']), claim_entries=len(ledger['claims']), certificate_bundles=7, certificate_files=28, complete_cover_hashes=3, fresh_drat_run=False, scope='Byte consistency only; not formal encoder or cover verification.')
print(json.dumps(result, indent=2))
