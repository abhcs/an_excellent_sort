"""compare.py TOK.txt ORIGINAL.jsonl: outcomes and node counts of tok.c against the original token search
(tokcore2.c, positional cone on).  Node counts of a refuted prefix are complete counts of layers 4 and 5
within the bounds, so two correct implementations must agree on them exactly."""
import json, sys
mine = {}
for line in open(sys.argv[1]):
    f = line.split(); k = next(i for i, x in enumerate(f) if not x.lstrip('-').isdigit())
    mine[int(f[0])] = (list(map(int, f[1:k])), f[k], float(line.split()[-1]))
orig = {json.loads(l)['idx']: json.loads(l) for l in open(sys.argv[2])}
same_out = same_nodes = 0; diff = []
for i, o in orig.items():
    nodes, out, sec = mine[i]
    ok_out = (out == 'refuted') == (o['outcome'] == 'none'); same_out += ok_out
    ok_nodes = nodes == o['nodes']; same_nodes += ok_nodes
    if not (ok_out and ok_nodes):
        diff.append((i, nodes, out, o['nodes'], o['outcome']))
print(f'{len(orig)} prefixes; tok.c refutes {sum(1 for v in mine.values() if v[1] == "refuted")}, '
      f'finds a sorter for {sum(1 for v in mine.values() if v[1] == "SORTER")}; '
      f'same outcome {same_out}, same node counts {same_nodes}')
print(f'CPU time: tok.c {sum(v[2] for v in mine.values()) / 3600:.2f} h, original {sum(o["seconds"] for o in orig.values()) / 3600:.2f} h (wall per job)')
for d in diff[:10]:
    print('DIFF', d)
