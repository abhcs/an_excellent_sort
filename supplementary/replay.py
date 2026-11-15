"""Replay the finite checks used in this report, leaving archived inputs intact."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix="mathathon-replay-") as temporary:
    work = Path(temporary)
    # These replayers need text/JSON inputs, not the large SAT proof traces.
    shutil.copytree(HERE / "research", work / "research", ignore=shutil.ignore_patterns("*.cnf", "*.drat"))
    shutil.copytree(HERE / "constructions", work / "constructions")
    shutil.copytree(HERE / "asymptotic", work / "asymptotic")
    (work / "collaborator").mkdir()
    shutil.copy2(HERE / "collaborator/sorting_network_depth_bound-source.txt", work / "collaborator/sorting_network_depth_bound-source.txt")
    commands = [
        ("research", ["depth-hand-proofs/verify/profile_transfer.py", "--max-n", "11"]),
        ("research", ["depth-hand-proofs/verify/h7_profiles_proof.py", "--out", str(work / "h7-check.json")]),
        ("research", ["d18-search/verify_restriction_structure.py", "--replay"]),
        ("research", ["d18-search/commuting_prefix_hand_verify.py"]),
        ("research", ["depth-hand-proofs/verify/h9_cycle_proof.py", "--out", str(work / "cycle-check.json")]),
        ("research", ["depth-hand-proofs/verify/h9_round2_case1_branch_check.py"]),
        ("research", ["depth-hand-proofs/verify/h9_root_helper_case3.py"]),
        ("research", ["depth-hand-proofs/verify/h9_feedback_round2_proof.py"]),
        ("research", ["depth-hand-proofs/verify/h9_feedback_round3_merge333.py"]),
        ("research", ["d18-search/merge_component_verify.py"]),
        ("constructions", ["build.py"]),
        ("constructions", ["verify.py", "net_128.json"]),
        ("constructions", ["verify.py", "net_1024.json"]),
        ("constructions", ["extend_and_verify.py"]),
        ("asymptotic", ["verify_chvatal_parameters.py"]),
    ]
    for directory, arguments in commands:
        python = os.environ.get("MATHATHON_COMPONENT_PYTHON", sys.executable) if arguments[0].endswith("merge_component_verify.py") else sys.executable
        print(json.dumps({"cwd": directory, "command": [python, *arguments]}), flush=True)
        subprocess.run([python, *arguments], cwd=work / directory, check=True)
print("All selected replays passed.")
