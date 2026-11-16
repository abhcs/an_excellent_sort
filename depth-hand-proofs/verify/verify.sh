#!/bin/sh
# Re-run every check behind depth-hand-proofs/README.md and h9.md (needs cc and python3; the
# python-sat checks of h9.md run too when .venv exists, adding about half a minute).
set -e
cd "$(dirname "$0")"
cc -O2 -o small_facts small_facts.c
cc -O2 -o blinding blinding.c
echo "== base facts, brute force over all layer shapes (no maximality assumed)"
./small_facts 3 1 1           # D(3) >= 3
./small_facts 5 2 2 2 2       # D(5) >= 5
./small_facts 5 1 1 2 2 2     # Lemma 3
./small_facts 5 1 2 2 2 2     # contrast: one thin layer is possible
echo "== Lemma 1 (two-layer blinding), every second layer, n = 3..11"
for n in 3 4 5 6 7 8 9 10 11; do ./blinding $n 2 $((n / 2)); done
echo "== Lemma 3(b) and Lemma 4"
python3 lemma3_case_b.py
python3 lemma4_two_sentinels.py
echo "== the constructions on actual sorting networks"
python3 mechanism.py
echo "== T3 is false"
python3 t3_counterexample.py
echo "== where blinding stops (data for section 6)"
./blinding 7 3 4
./blinding 9 3 4 3 3
echo "== (H9) by the case tree, no SAT (h9.md sections 4-5)"
cc -O2 -o h9_blind h9_blind.c
cc -O2 -o h9_tree h9_tree.c
./h9_blind
./h9_tree -r -n -p
python3 h9_ending_certificates.py --verify ../results/h9-ending-certificates.json
echo "== (H9): the hand proofs of section 7, and the proof of (P7) as written in h9.md"
cc -O2 -o h9_hand h9_hand.c
cc -O2 -o h9_p7 h9_p7.c
./h9_hand
./h9_p7
python3 h9_p7_proof.py
python3 h9_cycle_proof.py --out ../results/h9-cycle-proof-checks.json
python3 h7_profiles_proof.py --out ../results/h7-profiles-proof.json
python3 h9_feedback_commute_proof.py --out ../results/h9-feedback-commute-proof.json
python3 h9_feedback_reschedule_proof.py --out ../results/h9-feedback-reschedule-proof.json
python3 h9_feedback_next_proof.py --out ../results/h9-feedback-next-proof.json
python3 h9_feedback_next_078.py --out ../results/h9-feedback-next-078.json
python3 h9_feedback_round2_proof.py
python3 h9_round2_case1_branch_check.py
python3 h9_root_helper_case3.py
python3 h9_feedback_round3_merge333.py
python3 h9_feedback_round4_proof.py
python3 h9_feedback_round5_proof.py
python3 h9_feedback_round6_proof.py
python3 h9_feedback_round7_proof.py
python3 h9_feedback_round9_proof.py
echo "== beyond (H9): D(13) (h9.md section 9)"
cc -O2 -o leak_blinding leak_blinding.c
./leak_blinding 11 6 0       # reproduces the 11-channel count of section 6
./leak_blinding 13 6 0       # three blind layers, what D(7) >= 6 needs
./leak_blinding 13 6 1       # at most one leak, what (P7) needs
python3 d13_networks.py
if [ -x .venv/bin/python ]; then
    echo "== (H9): SAT encoding and certificate checks (h9.md sections 3-4; uses .venv with python-sat)"
    .venv/bin/python h9_validate.py
    .venv/bin/python h9_certs_check.py 10
else
    echo "(skipping the python-sat checks of h9.md: no .venv; see h9.md section 9)"
fi
echo "all checks passed"
