#!/usr/bin/env python3
"""Exact synthesis via a matching with local width-two output constraints."""
import argparse,hashlib,json,time
from pathlib import Path
import netsat
from netsat import prefix_images,apply_layers,verify_all
from probe_frontier import ProbeModel
from prefix_drat import RecordingSolver
from two_layer_matching_ending import add_matching_ending
from d13_feedback_round9_data_dp import profiles,ending
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seed',type=Path,required=True)
    ap.add_argument('--depth',type=int,required=True)
    ap.add_argument('--witness',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();started=time.monotonic()
    data=json.loads(args.seed.read_text());n=data['n'];prefix=data['prefix']
    free=args.depth-len(prefix)-2;assert free>=0
    universe=sorted(prefix_images(n,prefix));netsat.Solver=RecordingSolver
    model=ProbeModel(n,free+2,universe,phi=False,nored0=False)
    # These tail variables merely reserve unrestricted earlier simulation
    # layers in ProbeModel. The separate automaton chooses the actual ending.
    for layer in model.g[free+1:]:
        for v in layer.values():model.add([-v])
    if args.witness:
        network=json.loads(args.witness.read_text())['layers']
        assert len(network)==args.depth and network[:len(prefix)]==prefix and verify_all(n,network)
        for t,layer in enumerate(network[len(prefix):args.depth-2]):
            selected=set(map(tuple,layer));assert selected<=set(model.g[t])
            for e,v in model.g[t].items():model.add([v if e in selected else -v])
    states={x:model.simulate_to_cut(x,free) for x in universe}
    path_stats=add_matching_ending(model,states)
    folder=args.out.with_suffix('');folder.mkdir(parents=True,exist_ok=True)
    cnf=folder/'problem.cnf';proof=folder/'proof.drat'
    cnf.write_text(f'p cnf {model.nv} {len(model.S.clauses)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in model.S.clauses))
    result=dict(status='BUILT',n=n,depth=args.depth,cut=args.depth-2,prefix=prefix,
                inputs=len(universe),variables=model.nv,clauses=model.ncl,matching_ending=path_stats,
                source_sha256=sha(Path(__file__)),seed_sha256=sha(args.seed),
                cnf_sha256=sha(cnf),certificate_directory=str(folder),
                dependencies_sha256={name:sha(HERE/name) for name in ['netsat.py','probe_frontier.py','prefix_drat.py','two_layer_matching_ending.py','d13_feedback_round9_data_dp.py']},
                scope='Exact sorting completion of the fixed actual prefix using the span-three adjacent ending normal form')
    def save():result['seconds']=time.monotonic()-started;args.out.write_text(json.dumps(result,indent=2)+'\n')
    save();print(json.dumps({k:v for k,v in result.items() if k not in ('prefix','dependencies_sha256')}),flush=True)
    try:
        sat=model.S.solve()
        if sat:
            layers=model.network(model.S.get_model())[:free]
            cut_states=sorted({apply_layers(layers,x) for x in universe})
            tail,stats=ending(profiles([[bool(x>>i&1) for i in range(n)] for x in cut_states]))
            assert tail is not None and verify_all(n,prefix+layers+tail)
            result.update(status='SORTER',layers=prefix+layers+tail,all_binary_inputs_verified=True,independent_ending_stats=stats)
        else:
            proof.write_text('\n'.join(model.S.get_proof())+'\n')
            result.update(status='UNSAT_UNCHECKED',proof_sha256=sha(proof))
        save();print(json.dumps(dict(status=result['status'],seconds=result['seconds'])),flush=True)
    finally:model.S.delete()
if __name__=='__main__':main()
