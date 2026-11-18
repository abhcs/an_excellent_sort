#!/usr/bin/env python3
"""Two bounded nine-wire residuals for the second-layer-three theorem."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import netsat
from pysat.solvers import Solver

ROOT = Path(__file__).parent
CHECKER_COMMIT = "2e3b2dc0ecf938addbd779d42877b6ed69d9a985"
PREFIXES = {
    "UU": [[(0, 1), (2, 3), (4, 5), (6, 7)], [(0, 2), (4, 6)]],
    "UD": [[(0, 1), (2, 3), (4, 5), (6, 7)], [(0, 2), (5, 7)]],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RecordingSolver:
    def __init__(self, name):
        self.inner = Solver(name=name, with_proof=True)
        self.clauses = []

    def add_clause(self, clause):
        self.clauses.append(list(clause))
        self.inner.add_clause(clause)

    def __getattr__(self, name):
        return getattr(self.inner, name)


def build(case):
    prefix = PREFIXES[case]
    universe = sorted(x for x in netsat.prefix_images(9, prefix)
                      if not netsat.is_sorted(x, 9))
    original = netsat.Solver
    try:
        netsat.Solver = RecordingSolver
        model = netsat.Model(9, 5, universe, sym=False, phi=True,
                             cosat=False, nored0=False, lex=False,
                             solver="cadical195")
    finally:
        netsat.Solver = original
    for x in universe:
        model.add_input(x)
    return model, universe


def cnf_bytes(model):
    rows = [f"p cnf {model.nv} {len(model.S.clauses)}"]
    rows += [" ".join(map(str, c)) + " 0" for c in model.S.clauses]
    return ("\n".join(rows) + "\n").encode()


def worker(case, out):
    model, universe = build(case)
    try:
        cnf = out / "problem.cnf"
        cnf.write_bytes(cnf_bytes(model))
        result = {
            "case": case, "n": 9, "prefix": PREFIXES[case], "suffix_depth": 5,
            "unsorted_image_count": len(universe), "variables": model.nv,
            "clauses": len(model.S.clauses), "solver": "cadical195",
            "options": {"phi": True, "sym": False, "cosat": False,
                        "nored0": False, "lex": False},
            "cnf_sha256": sha(cnf), "source_sha256": sha(Path(__file__)),
            "encoder_sha256": sha(Path(netsat.__file__)), "status": "BUILT",
            "independently_proof_checked": False,
        }
        destination = out / "result.json"
        destination.write_text(json.dumps(result, indent=2) + "\n")
        started = time.monotonic()
        sat = model.S.solve()
        result["solve_seconds"] = time.monotonic() - started
        if sat:
            result["status"] = "SAT"
            result["network"] = PREFIXES[case] + model.network(model.S.get_model())
            assert netsat.verify_all(9, result["network"])
            result["direct_binary_inputs_checked"] = 512
        else:
            result["status"] = "UNSAT_UNCHECKED"
            proof = out / "proof.drat"
            proof.write_text("\n".join(model.S.get_proof()) + "\n")
            result["proof_sha256"] = sha(proof)
        destination.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result), flush=True)
    finally:
        model.S.delete()


def bounded(command, cap, log):
    started = time.monotonic()
    try:
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, timeout=cap, check=False)
        log.write_text(process.stdout)
        return {"terminal": True, "timeout": False, "returncode": process.returncode,
                "wall_seconds": time.monotonic() - started, "cap_seconds": cap,
                "command": command}
    except subprocess.TimeoutExpired as error:
        output = error.stdout or b""
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
        log.write_text(output)
        return {"terminal": True, "timeout": True, "returncode": None,
                "wall_seconds": time.monotonic() - started, "cap_seconds": cap,
                "command": command}


def batch(checker):
    summary = {"scope": "Two nine-wire finite lemmas only; no seventeen-wire cover solve.",
               "cases": [], "all_jobs_terminal": False}
    for case in PREFIXES:
        out = ROOT / "results" / f"d17-second-recovery-{case.lower()}"
        out.mkdir(exist_ok=False)
        solve = bounded([sys.executable, str(Path(__file__).resolve()), "--worker", case,
                         "--out", str(out.resolve())], 10, out / "solve.log")
        (out / "solve-terminal.json").write_text(json.dumps(solve, indent=2) + "\n")
        record = {"case": case, "solve_terminal": solve}
        if not solve["timeout"] and solve["returncode"] == 0:
            result = json.loads((out / "result.json").read_text())
            if result["status"] == "UNSAT_UNCHECKED":
                check = bounded([str(checker.resolve()), str((out / "problem.cnf").resolve()),
                                 str((out / "proof.drat").resolve()), "-t", "10"],
                                10, out / "check.log")
                (out / "check-terminal.json").write_text(json.dumps(check, indent=2) + "\n")
                accepted = (not check["timeout"] and check["returncode"] == 0 and
                            "s VERIFIED" in (out / "check.log").read_text())
                result.update({"status": "UNSAT_CHECKED" if accepted else "CHECK_FAILED",
                               "independently_proof_checked": accepted,
                               "checker_upstream": "https://github.com/marijnheule/drat-trim.git",
                               "checker_commit": CHECKER_COMMIT,
                               "checker_binary_sha256": sha(checker),
                               "checker_source_sha256": sha(checker.parent / "drat-trim.c"),
                               "check_seconds": check["wall_seconds"]})
                (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
                record["check_terminal"] = check
            record["result"] = result
        summary["cases"].append(record)
    summary["all_jobs_terminal"] = True
    summary["both_residuals_checked_unsat"] = all(
        r.get("result", {}).get("status") == "UNSAT_CHECKED" for r in summary["cases"])
    destination = ROOT / "results" / "d17-second-recovery-batch.json"
    destination.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=PREFIXES)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--checker", type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker, args.out)
    else:
        assert args.checker and args.checker.is_file()
        batch(args.checker)


if __name__ == "__main__":
    main()
