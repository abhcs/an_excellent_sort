"""Block-separable certificates for every prefix of a file; writes one JSON line per prefix and a summary.
usage: EXC.json KEY OUT.jsonl"""
import json, sys, time, collections
sys.path[:0] = ['.']
import blockcert_fast as bc
d = json.load(open(sys.argv[1])); P = d[sys.argv[2]]
t = time.time(); vals = collections.Counter(); bad = []
with open(sys.argv[3], 'w') as fo:
    for i, pre in enumerate(P):
        cert = bc.certify(pre); ok, val = bc.check(cert)
        good = ok and cert['value'] > 12
        vals[round(float(cert['value']), 3) if ok else 'check failed'] += 1
        if not good:
            bad.append(i)
        fo.write(json.dumps({'idx': i, 'sum_pi': str(cert['value']), 'ok': ok, 'pi': [str(v) for v in cert['pi']],
                             'c': {o[1]: str(v) for o, v in zip(cert['outs'], cert['c'])}}) + '\n')
print(f'{len(P)} prefixes ({time.time()-t:.0f}s); not proved: {len(bad)} {bad[:20]}')
print('least sum of potentials:', min(v for v in vals if v != 'check failed'))
