"""Negative tests for the descent rules in check_facts.py: copies a proved store, tampers with one
thing, and expects the checker to fail; also re-solves a few certificates with --resat.
usage: STORE STATEMENT"""
import json, os, shutil, subprocess, sys, tempfile
src, stmt = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, '..', 'check_facts.py')


def facts_files(d):
    return [os.path.join(d, f) for f in os.listdir(d) if f.startswith('facts-') and f.endswith('.jsonl')]


def run(d, extra=()):
    p = subprocess.run([sys.executable, CHECK, d, stmt, *extra], capture_output=True, text=True)
    last = [l for l in p.stdout.splitlines() if l.strip()][-1]
    return last


def tamper(name, fn):
    d = tempfile.mkdtemp()
    for f in os.listdir(src):
        if f != 'verified.txt' and os.path.isfile(os.path.join(src, f)):
            shutil.copy(os.path.join(src, f), d)
    changed = fn(d)
    res = run(d) if changed else 'nothing to tamper'
    ok = changed and ' 0 failed' not in res
    print(f'{"PASS" if ok else "FAIL"} {name}: {res}')
    shutil.rmtree(d)
    return ok


def edit_first(d, pred, change):
    for fn in facts_files(d):
        lines = open(fn).read().splitlines(True)
        for k, line in enumerate(lines):
            f = json.loads(line)
            if pred(f):
                change(f)
                lines[k] = json.dumps(f) + '\n'
                open(fn, 'w').write(''.join(lines))
                return True
    return False


def bad_hash(d):
    def ch(f):
        f['step']['cnf_sha256'] = '0' * 64
    return edit_first(d, lambda f: f.get('step', {}).get('rule') == 'sat', ch)


def no_record(d):
    recs = open(os.path.join(d, 'sat_certs.jsonl')).read().splitlines(True)
    open(os.path.join(d, 'sat_certs.jsonl'), 'w').write(''.join(recs[1:]))   # drop the first record
    return bool(recs)


def drop_qcovers(d):
    def ch(f):
        f['step']['qcovers'] = []
    return edit_first(d, lambda f: f.get('step', {}).get('rule') == 'split' and f['step'].get('qcovers'), ch)


results = [tamper('sat fact with a wrong CNF hash', bad_hash),
           tamper('sat fact whose certificate record is missing', no_record),
           tamper('split whose sentinel covers are removed', drop_qcovers)]
print('clean store:', run(src))
d = tempfile.mkdtemp()
for f in os.listdir(src):
    if f != 'verified.txt' and os.path.isfile(os.path.join(src, f)):
        shutil.copy(os.path.join(src, f), d)
print('re-solved (--resat):', run(d, ('--resat', '--jobs', '4')))
shutil.rmtree(d)
print('ALL NEGATIVE TESTS PASS' if all(results) else 'SOME NEGATIVE TEST FAILED')
