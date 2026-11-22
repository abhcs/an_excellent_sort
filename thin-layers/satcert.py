"""satcert.py -- SAT certificates for prover nodes (README §8.15).

A node (n, prefix, t, caps) claims: no t further layers (layer i at most caps[i] comparators) make
the prefix a sorting network.  Its certificate is a CNF in netsat's encoding together with a DRAT
proof of unsatisfiability that drat-trim verified:

  * the CNF is generated deterministically from the node alone (node_cnf): netsat.Model with t free
    layers and every unsorted output of the prefix, in increasing order, and a sequential-counter
    "at most caps[i]" on free layer i.  The model's restrictions (standard comparators, no redundant
    comparator in the free layers, the end-game constraints of Codish, Cruz-Filipe and
    Schneider-Kamp) each hold in some completion whenever one exists (d18-search/netsat.py), so an
    UNSAT CNF means the node has no completion;
  * certify() solves it with the standalone CaDiCaL writing a DRAT proof and checks the proof with
    drat-trim.  The proof is deleted after the check; the record keeps the CNF's sha256.

Records are JSON lines in STORE/sat_certs.jsonl.  check_facts.py regenerates each certified node's
CNF, compares the sha256 and accepts the recorded drat-trim verdict, or re-solves and re-checks it
with --resat.

Tools: CADICAL and DRATTRIM environment variables, else `cadical` / `drat-trim` on PATH, else
../build/drat-trim/drat-trim for drat-trim.  SATCERT_TMP: directory for the CNF and proof files
(default the system temp directory; a 14-channel node needs about 10 MB of CNF and 100 MB of proof).
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'd18-search'))
import netsat                                            # noqa: E402

ENC = 'netsat-full-v1'


def _tool(env, name, fallbacks=()):
    p = os.environ.get(env)
    if p:
        return p
    p = shutil.which(name)
    if p:
        return p
    for f in fallbacks:
        if os.path.exists(f):
            return f
    return None


CADICAL = _tool('CADICAL', 'cadical', [os.path.expanduser('~/.elan/toolchains/leanprover--lean4---v4.35.0/bin/cadical')])
DRATTRIM = _tool('DRATTRIM', 'drat-trim', [os.path.join(HERE, '..', 'build', 'drat-trim', 'drat-trim')])


class _CNF(netsat.Model):
    """netsat.Model that records clauses instead of solving."""

    def __init__(self, *a, **kw):
        self.rec = []
        kw['solver'] = 'minisat22'
        super().__init__(*a, **kw)

    def add(self, cl):
        out = []
        for l in cl:
            if l is True:
                return
            if l is False:
                continue
            out.append(l)
        if not out:
            v = self.new_var()
            self.rec.append([v])
            self.rec.append([-v])
            self.ncl += 2
            return
        self.rec.append(out)
        self.ncl += 1


def norm_prefix(layers):
    return [[[int(i), int(j)] for i, j in L] for L in layers]


def node_key(n, layers, t, caps):
    return json.dumps([n, t, list(caps), norm_prefix(layers)], separators=(',', ':'))


def node_cnf(n, layers, t, caps=()):
    """(DIMACS text, sha256 hex, model).  Deterministic in (n, layers, t, caps)."""
    from pysat.card import CardEnc, EncType
    prefix = [[tuple(c) for c in L] for L in layers]
    U = sorted(x for x in netsat.prefix_images(n, prefix) if not netsat.is_sorted(x, n))
    M = _CNF(n, t, U)
    for i, c in enumerate(caps):
        if i >= t:
            break
        lits = sorted(M.g[i].values())
        if not lits or c >= len(lits):
            continue
        enc = CardEnc.atmost(lits=lits, bound=c, top_id=M.nv, encoding=EncType.seqcounter)
        for cl in enc.clauses:
            M.add(cl)
        M.nv = max(M.nv, enc.nv)
    for x in U:
        M.add_input(x)
    head = [f'c {ENC} n={n} t={t} caps={json.dumps(list(caps))} prefix={json.dumps(norm_prefix(layers))}',
            f'p cnf {M.nv} {len(M.rec)}']
    text = '\n'.join(head + [' '.join(map(str, cl)) + ' 0' for cl in M.rec]) + '\n'
    return text, hashlib.sha256(text.encode()).hexdigest(), M


def certify(n, layers, t, caps=(), seconds=None, workdir=None, keep=False):
    """Solve the node's CNF with CaDiCaL (DRAT proof) and check the proof with drat-trim.
    Returns a record: result UNSAT (drat VERIFIED or the checker's complaint), SAT (with the
    completion found, verified on all inputs) or UNKNOWN (time limit)."""
    if CADICAL is None or DRATTRIM is None:
        raise RuntimeError(f'need CaDiCaL and drat-trim (CADICAL={CADICAL}, DRATTRIM={DRATTRIM})')
    t0 = time.time()
    text, sha, M = node_cnf(n, layers, t, caps)
    t_gen = time.time() - t0
    d = tempfile.mkdtemp(dir=workdir or os.environ.get('SATCERT_TMP'))
    cnf, proof = os.path.join(d, 'node.cnf'), os.path.join(d, 'node.drat')
    with open(cnf, 'w') as f:
        f.write(text)
    rec = {'key': node_key(n, layers, t, caps), 'enc': ENC, 'cnf_sha256': sha, 'vars': M.nv,
           'clauses': len(M.rec), 'gen_s': round(t_gen, 1), 'limit': seconds}
    cmd = [CADICAL, '-q', cnf, proof]
    if seconds:
        cmd[1:1] = ['-t', str(int(seconds))]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    rec['solve_s'] = round(time.time() - t0, 1)
    if p.returncode == 20:
        rec['result'] = 'UNSAT'
        rec['proof_bytes'] = os.path.getsize(proof)
        t0 = time.time()
        q = subprocess.run([DRATTRIM, cnf, proof, '-t', '1000000'], capture_output=True, text=True)
        rec['check_s'] = round(time.time() - t0, 1)
        out = q.stdout.replace('\r', '\n')
        rec['drat'] = 'VERIFIED' if '\ns VERIFIED' in '\n' + out else 'FAILED: ' + out[-200:]
    elif p.returncode == 10:
        pos = {int(v) for line in p.stdout.splitlines() if line.startswith('v ')
               for v in line[2:].split() if int(v) > 0}
        net = [sorted(pp for pp, v in M.g[i].items() if v in pos) for i in range(t)]
        full = [[tuple(c) for c in L] for L in layers] + net
        rec['result'] = 'SAT'
        rec['network'] = [[list(c) for c in L] for L in full]
        rec['network_sorts'] = netsat.verify_all(n, full)
    else:
        rec['result'] = 'UNKNOWN'
        rec['rc'] = p.returncode
    if not keep:
        shutil.rmtree(d, ignore_errors=True)
    rec['when'] = time.strftime('%Y-%m-%d %H:%M:%S')
    return rec


def load_records(path):
    """Records of STORE/sat_certs.jsonl by node key (later records win)."""
    out = {}
    fn = os.path.join(path, 'sat_certs.jsonl')
    if os.path.exists(fn):
        with open(fn) as f:
            for line in f:
                if line.endswith('\n') and line.strip():
                    r = json.loads(line)
                    out[r['key']] = r
    return out


def append_record(path, rec):
    with open(os.path.join(path, 'sat_certs.jsonl'), 'a') as f:
        f.write(json.dumps(rec) + '\n')
        f.flush()


if __name__ == '__main__':
    # self-test on a small node: 8 channels, Parberry first layer, 4 free layers (no 5-layer 8-sorter)
    n, L = 8, [[(0, 1), (2, 3), (4, 5), (6, 7)]]
    print('tools', CADICAL, DRATTRIM)
    print(json.dumps(certify(n, L, 4)))
    print(json.dumps({k: v for k, v in certify(n, L, 5).items() if k != 'network'}))
