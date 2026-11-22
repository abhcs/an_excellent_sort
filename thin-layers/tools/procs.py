#!/usr/bin/env python3
"""procs.py list|kill|stop|cont SCRIPT [ARG...]: select processes whose argv[1] has basename SCRIPT (a Python
script run by an interpreter) and whose following argv start with ARG...  Matching on argv fields,
not on the whole command line, so a shell whose command text mentions the script is never hit."""
import os, signal, subprocess, sys

action, script, want = sys.argv[1], sys.argv[2], sys.argv[3:]
out = subprocess.run(['ps', '-axww', '-o', 'pid=', '-o', 'command='], capture_output=True, text=True).stdout
hits = []
for line in out.splitlines():
    pid_s, _, cmd = line.strip().partition(' ')
    pid = int(pid_s)
    if pid == os.getpid():
        continue
    argv = cmd.split()
    if not argv:
        continue
    if script.endswith('.py'):
        if len(argv) < 2 or 'ython' not in os.path.basename(argv[0]):
            continue
        if os.path.basename(argv[1]) != script:
            continue
        if argv[2:2 + len(want)] != want:
            continue
    else:                                    # a binary: match the executable's basename
        if os.path.basename(argv[0]) != script or argv[1:1 + len(want)] != want:
            continue
    hits.append((pid, cmd[:150]))
for pid, cmd in hits:
    print(pid, cmd)
    if action == 'kill':
        os.kill(pid, signal.SIGTERM)
    elif action == 'stop':
        os.kill(pid, signal.SIGSTOP)
    elif action == 'cont':
        os.kill(pid, signal.SIGCONT)
print(f'{len(hits)} matched', file=sys.stderr)
