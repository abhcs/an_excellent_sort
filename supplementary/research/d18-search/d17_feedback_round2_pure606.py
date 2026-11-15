#!/usr/bin/env python3
"""Run the authorized 30s pure-606 probe and separate 30s DRAT check."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parent
PYTHON = '/Users/abhishek/Documents/an_excellent_sort/depth-hand-proofs/verify/.venv/bin/python'
CHECKER = Path('/private/tmp/d18-structural-drat-trim/drat-trim')
OUT = ROOT / 'results/d17-feedback-round2-pure606'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounded(name, command):
    started = time.monotonic()
    with (OUT / (name+'.log')).open('w') as log:
        process = subprocess.Popen(command, cwd=ROOT.parent, stdout=log,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        timed_out = False
        try:
            returncode = process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            returncode = process.wait()
    terminal = dict(status='TIMEOUT' if timed_out else 'COMPLETED', returncode=returncode,
                    elapsed_seconds=round(time.monotonic()-started,4), wall_limit_seconds=30,
                    process_terminal=True, command=list(map(str,command)))
    (OUT / (name+'-terminal.json')).write_text(json.dumps(terminal,indent=2)+'\n')
    print(json.dumps(dict(phase=name,**terminal)),flush=True)
    return terminal


def main():
    OUT.mkdir(parents=True,exist_ok=False)
    result_path = OUT / 'result.json'
    states = ROOT / 'results/d17-feedback-fourteen-hand606-states.json'
    solve = bounded('solve',[PYTHON,str(ROOT/'d17_feedback_fourteen.py'),
                            '--states',str(states),'--out',str(result_path),'--proof'])
    result = json.loads(result_path.read_text()) if result_path.exists() else {}
    audit = dict(status=result.get('status','NO_RESULT'), solve=solve,
                 states_sha256=digest(states), wrapper_sha256=digest(Path(__file__)),
                 independently_proof_checked=False, all_processes_terminal=True)
    if solve['status']=='COMPLETED' and solve['returncode']==0 and result.get('status')=='UNSAT':
        cert = result_path.with_suffix('')
        check = bounded('check',[str(CHECKER),str(cert/'problem.cnf'),str(cert/'proof.drat'),
                                 '-c',str(OUT/'core.cnf'),'-t','28'])
        verified = check['status']=='COMPLETED' and check['returncode']==0 and 's VERIFIED' in (OUT/'check.log').read_text()
        audit.update(check=check, independently_proof_checked=verified,
                     status='VERIFIED_UNSAT' if verified else 'UNSAT_UNCHECKED',
                     cnf_sha256=digest(cert/'problem.cnf'), proof_sha256=digest(cert/'proof.drat'),
                     checker_sha256=digest(CHECKER), source_sha256=result['source_sha256'],
                     library_sha256=result['library_sha256'], variables=result['variables'],
                     clauses=result['clauses'], family_size=result['family_size'])
    elif solve['status']=='TIMEOUT':
        audit['status']='TIMEOUT'
    (OUT/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2),flush=True)


if __name__=='__main__':
    main()
