#!/bin/zsh
# run_tok.sh IN.txt OUT.txt JOBS: tok.c on every line of IN.txt, JOBS processes (round-robin split), merged into OUT.txt
in=$1; out=$2; J=$3; dir=${out}.parts; mkdir -p $dir
for k in $(seq 0 $((J - 1))); do
  awk -v J=$J -v k=$k '(NR - 1) % J == k' $in > $dir/in_$k
  ( caffeinate -i ./tok < $dir/in_$k > $dir/out_$k ) &
done
wait
cat $dir/out_* | sort -n > $out
if [ $(wc -l < $out) -eq $(wc -l < $in) ]; then rm -r $dir; else echo "MISSING RESULTS: parts kept in $dir"; exit 1; fi
echo "done: $(wc -l < $out) results"
