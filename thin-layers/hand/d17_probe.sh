#!/bin/zsh
# d17_probe.sh WORKDIR: the two measurements behind "what does not carry over" from D(13) to D(17)
# (efficient-prefixes.md section 10). Intermediate files go to WORKDIR; the logs to ../logs:
#  1. logs/hand_d17_resid_12_3.log (about 7 minutes). Every class of the (12,3) family with its exceptional
#     members' residuals under all 2n sentinels, any track (excres.c), looked up among the classes of the proved
#     (11,2) family (classcount.c, exclookup.py). No exceptional-only class has a residual there.
#  2. logs/hand_d17_tok_12_3.log (about 7 minutes with 3 jobs, more on a busy machine). The exact token search
#     (tokcore2.c) on the first exceptional-only (12,3) class: capped, then on 100 random fourth layers searched to
#     the end (d17_tokrate.py).
set -e
setopt pipefail
cd ${0:A:h}
w=${1:?usage: d17_probe.sh WORKDIR}; mkdir -p $w
for t in classcount excres tokcore2; do cc -O3 -march=native -o $t $t.c; done
{
  python3 indep13/family.py ../results/l2classes_11_2.json > $w/spec_11_2.txt
  python3 indep13/family.py ../results/l2classes_12_3.json > $w/spec_12_3.txt
  echo "(11,2) family: $(./classcount $w/classes_11_2.bin < $w/spec_11_2.txt 2>/dev/null)"
  echo "(12,3) family: $(./excres $w/excres_12_3.txt < $w/spec_12_3.txt 2>/dev/null)"
  python3 exclookup.py $w/excres_12_3.txt $w/classes_11_2.bin $w/left_12_3.txt
  python3 -c "import json, sys; a = set(open(sys.argv[1]).read().split()); b = set(json.load(open(sys.argv[2]))['hash']); \
print(f'the {len(a)} remaining classes are those of {sys.argv[2]}: {a == b}')" $w/left_12_3.txt exconly_12_3.json
} 2>&1 | tee ../logs/hand_d17_resid_12_3.log
python3 d17_tokrate.py exconly_12_3.json 0 100 1 2>&1 | tee ../logs/hand_d17_tok_12_3.log
