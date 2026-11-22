#!/usr/bin/env python3
"""descent_init.py -- a fresh fact store holding chosen statements and every fact their proofs use.

  descent_init.py export SRC_STORE OUT_PREFIX [--exclude ST,ST,...]
      write OUT_PREFIX_facts.jsonl.gz and OUT_PREFIX_statements.jsonl: the recorded statements of
      SRC_STORE (minus --exclude) and the dependency closure of their facts
  descent_init.py init OUT_PREFIX STORE
      create STORE from such an export (STORE must not exist yet)

The descent run (README §8.15) needs D(3..11) for the quick rule and the small sparse-start lemmas;
the committed export results/descent_base_* holds them (S11 = SS(11,8,4,3), whose proof needs
382,000 facts, is left out: the descent does not use it).  check_facts.py STORE re-checks the
imported facts from definitions.
"""
import gzip, json, os, sys


def closure(facts, roots):
    need, stack = set(), list(roots)
    while stack:
        fid = stack.pop()
        if fid in need:
            continue
        need.add(fid)
        st = facts[fid].get('step', {})
        for key in ('child', 'lemma', 'of'):
            if key in st:
                stack.append(st[key])
        stack.extend(st.get('children', []))
        stack.extend(tr['node'] for tr in st.get('tracks', []))
        stack.extend(cv['node'] for cv in st.get('covers', []))
        stack.extend(q['fact'] for q in st.get('qcovers', []) if 'fact' in q)
    return need


def main():
    args = sys.argv[1:]
    exclude = set()
    if '--exclude' in args:
        k = args.index('--exclude')
        exclude = set(args[k + 1].split(';'))
        del args[k:k + 2]
    mode = args[0]
    if mode == 'export':
        src, out = args[1], args[2]
        stmts = [json.loads(l) for l in open(os.path.join(src, 'statements.jsonl')) if l.strip()]
        stmts = [s for s in stmts if s['statement'] not in exclude]
        lines, facts = {}, {}
        for fn in sorted(os.listdir(src)):
            if fn.startswith('facts-') and fn.endswith('.jsonl'):
                for line in open(os.path.join(src, fn)):
                    if line.endswith('\n') and line.strip():
                        f = json.loads(line)
                        facts[f['id']] = f
                        lines[f['id']] = line
        need = closure(facts, [s['fact'] for s in stmts])
        with gzip.open(out + '_facts.jsonl.gz', 'wt') as f:
            for fid in sorted(need):
                f.write(lines[fid])
        with open(out + '_statements.jsonl', 'w') as f:
            for s in stmts:
                f.write(json.dumps(s) + '\n')
        print(f'{len(stmts)} statements, {len(need)} facts -> {out}_facts.jsonl.gz '
              f'({os.path.getsize(out + "_facts.jsonl.gz") >> 10} KB)')
    elif mode == 'init':
        out, store = args[1], args[2]
        os.makedirs(store)
        with gzip.open(out + '_facts.jsonl.gz', 'rt') as f, open(os.path.join(store, 'facts-00000000-base.jsonl'), 'w') as g:
            k = 0
            for line in f:
                g.write(line)
                k += 1
        with open(out + '_statements.jsonl') as f, open(os.path.join(store, 'statements.jsonl'), 'w') as g:
            g.write(f.read())
        print(f'{store}: {k} facts')
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == '__main__':
    main()
