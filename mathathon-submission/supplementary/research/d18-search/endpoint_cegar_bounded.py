#!/usr/bin/env python3
"""Bound one incremental run and, on UNSAT, independently check its DRAT proof."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--seconds',type=float,default=60)
    parser.add_argument('--checker',type=Path)
    parser.add_argument('args',nargs=argparse.REMAINDER)
    args = parser.parse_args()
    assert not args.out.exists(), 'Use a fresh output file.'
    child_args = args.args[1:] if args.args[:1] == ['--'] else args.args
    command = [sys.executable,str(Path(__file__).with_name('endpoint_cegar.py')),
               '--out',str(args.out), '--seconds',str(max(1,args.seconds-3)),*child_args]
    if args.checker:
        command.append('--proof')
    start = time.monotonic()
    terminal = dict(command=command,wall_cap_seconds=args.seconds)
    with args.out.with_suffix('.log').open('w') as log:
        try:
            process = subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=args.seconds)
            terminal.update(terminal='EXITED',returncode=process.returncode)
        except subprocess.TimeoutExpired:
            terminal.update(terminal='TIME_LIMIT_KILLED_AND_REAPED',returncode=None)
    terminal['wall_seconds'] = time.monotonic()-start
    result = json.loads(args.out.read_text()) if args.out.exists() else {}
    if terminal['terminal'] != 'EXITED':
        result['status'] = 'TIME_LIMIT'
    elif terminal['returncode'] != 0:
        result['status'] = 'ERROR'
    if result.get('status') == 'UNSAT' and args.checker:
        directory = Path(result['certificate_directory'])
        command = [str(args.checker.resolve()),str(directory/'problem.cnf'),
                   str(directory/'proof.drat'),'-t',str(int(args.seconds)),
                   '-c',str(directory/'core.cnf')]
        start = time.monotonic()
        try:
            checked = subprocess.run(command,capture_output=True,text=True,timeout=args.seconds)
            (directory/'check.log').write_text(checked.stdout+checked.stderr)
            result.update(checker_returncode=checked.returncode,
                          independently_proof_checked=checked.returncode==0 and 's VERIFIED' in checked.stdout,
                          checker_sha256=hashlib.sha256(args.checker.read_bytes()).hexdigest())
        except subprocess.TimeoutExpired:
            result.update(independently_proof_checked=False,checker_terminal='TIME_LIMIT_KILLED_AND_REAPED')
        result['check_seconds'] = time.monotonic()-start
    result['worker_terminal'] = terminal
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()
                      if k not in ('prefix','selected_inputs','iterations','free_layers','intervals')}),flush=True)


if __name__ == '__main__':
    main()
