#!/usr/bin/env python3
"""Audit labels and padding identities; project the two checked families.

This does not run SAT or DRAT. Existing certificate manifests are checked
against their artifacts, and direct type replay corroborates padding.
"""
import hashlib
import json
from pathlib import Path
import random
import time

ROOT = Path(__file__).parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(state, layers):
    cur = list(state)
    counts = []
    for layer in layers:
        endpoints = [v for e in layer for v in e]
        assert len(endpoints) == len(set(endpoints))
        counts.append(sum(cur[a] == cur[b] == 0 for a,b in layer))
        for a,b in layer:
            cur[a],cur[b] = sorted((cur[a],cur[b]))
    return counts,cur


def sample_layer(n, rng):
    order = list(range(n))
    rng.shuffle(order)
    size = rng.randrange(n//2+1)
    return [tuple(sorted(order[2*i:2*i+2])) for i in range(size)]


def main():
    started = time.monotonic()
    records = []
    direct_checks = 0
    rng = random.Random(606608)
    for case, filename, auditname, certname in [
        (606,'d17-feedback-fourteen-hand606-states.json','d17-feedback-round2-pure606/audit.json',
         'd17-feedback-round2-pure606/result'),
        (608,'d17-feedback-fourteen-states.json','d17-feedback-fourteen-audit.json',
         'd17-feedback-fourteen-main/result')]:
        source = ROOT/'results'/filename
        supplied = json.loads(source.read_text())
        states = supplied['states']
        original = supplied['compact_to_original']
        auditpath = ROOT/'results'/auditname
        audit = json.loads(auditpath.read_text())
        cert = ROOT/'results'/certname
        assert audit['independently_proof_checked']
        assert audit['cnf_sha256'] == digest(cert/'problem.cnf')
        assert audit['proof_sha256'] == digest(cert/'proof.drat')
        assert audit['states_sha256'] == digest(source)
        assert len(states) == 20 and all(len(s)==14 and s.count(0)==9 for s in states)
        assert [i for i in range(14) if all(s[i]==0 for s in states)] == [0,1]
        assert original[:2] == [1,2]
        for real_count, deleted, extra in [(7,(0,1),1),(8,(0,),0)]:
            retained = [i for i in range(14) if i not in deleted]
            projected = [[s[i] for i in retained] for s in states]
            n = len(retained)
            assert n == real_count+5
            assert all(s.count(0)==real_count for s in projected)
            layers_to_check = [([],[])]
            layers_to_check += [(sample_layer(n,rng),sample_layer(n,rng)) for _ in range(200)]
            for layers in layers_to_check:
                lifted = [[tuple(retained[v] for v in e) for e in layer] for layer in layers]
                if len(deleted)==2:
                    for layer in lifted:
                        layer.append((0,1))
                for old,small in zip(states,projected):
                    before,out_small = run(small,layers)
                    after,out_old = run(old,lifted)
                    assert after == [x+extra for x in before]
                    assert [out_old[v] for v in retained] == out_small
                    assert all(out_old[v]==0 for v in deleted)
                    direct_checks += 1
            target = ROOT/f'results/d17-feedback-round2-case{case}-real{real_count}-states.json'
            record = dict(source_case=case, n=n, real_count=real_count, peak=real_count//2,
                          compact_to_original=[original[i] for i in retained],
                          retained_parent_coordinates=retained, deleted_common_real_coordinates=list(deleted),
                          source_states_path=str(source.relative_to(ROOT)), source_states_sha256=digest(source),
                          computational_premise=str(auditpath.relative_to(ROOT)), states=projected)
            target.write_text(json.dumps(record,indent=2)+'\n')
            records.append(dict(case=case,n=n,reals=real_count,peak=real_count//2,
                                projected_states=str(target.relative_to(ROOT)), projected_sha256=digest(target),
                                compact_to_original=record['compact_to_original'],
                                premise_audit=str(auditpath.relative_to(ROOT)), premise_audit_sha256=digest(auditpath)))
    result = dict(status='VERIFIED', solver_invoked=False, proof_checker_invoked=False,
                  source_sha256=digest(Path(__file__)), direct_padding_checks=direct_checks,
                  projected_families=records, computational_premises_retained=True,
                  new_D18_prefix_closure=False, elapsed_seconds=round(time.monotonic()-started,4))
    (ROOT/'results/d17-feedback-round2-padding.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
