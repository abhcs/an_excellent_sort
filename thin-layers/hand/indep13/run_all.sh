#!/bin/zsh
# run_all.sh OUTDIR [JOBS]: the independent check of the D(13) proof (efficient-prefixes.md section 9.2), end to end.
# About 8 CPU-hours for the token searches (an hour on 10 cores), two minutes for the class and residual check.
# Inputs: results/l2classes_11_4.json (second-layer classes), hand/reps_10_3.json and hand/direct_11_4.json (the
# 10- and 11-channel prefixes offered as lemmas; any prefixes would do, only those tok.c refutes are used).
set -e
cd ${0:A:h}
out=${1:?usage: run_all.sh OUTDIR [JOBS]}; J=${2:-10}; mkdir -p $out
cc -O3 -march=native -o tok tok.c
cc -O3 -march=native -o cls cls.c
python3 ../../verify_cover.py ../../results/l2classes_11_4.json
python3 family.py ../../results/l2classes_11_4.json > $out/family_11_4.txt
python3 prep.py ../reps_10_3.json $(python3 -c "import json; print(' '.join(str(json.loads(l)['idx']) for l in open('../../logs/hand_tok10_d13.jsonl')))") > $out/in10.txt
python3 prep.py ../direct_11_4.json > $out/in11.txt
./run_tok.sh $out/in11.txt $out/tok11.txt $J
./run_tok.sh $out/in10.txt $out/tok10.txt $J
python3 checksorter.py $out/in10.txt $out/tok10.txt | tail -1
for k in 10 11; do
  awk 'NR == FNR { if ($0 ~ / refuted /) ok[$1] = 1; next } ($1 in ok)' $out/tok$k.txt $out/in$k.txt > $out/lemmas$k.txt
done
wc -l $out/lemmas10.txt $out/lemmas11.txt
./cls $out/family_11_4.txt $out/lemmas10.txt $out/lemmas11.txt $out/witness.tsv $out/members.txt
python3 wcheck.py $out/family_11_4.txt $out/witness.tsv $out/members.txt $out/lemmas10.txt $out/lemmas11.txt 1000 1
ONLY=direct python3 wcheck.py $out/family_11_4.txt $out/witness.tsv $out/members.txt $out/lemmas10.txt $out/lemmas11.txt 1000 1
