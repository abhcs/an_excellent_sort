#!/usr/bin/env python3
"""Independent source review controls and checked-CNF bindings; no SAT calls."""
import gzip
import hashlib
import importlib.util
import itertools
import json
import sys
import tempfile
import time
from pathlib import Path

from d17_feedback_round9_check import states_of, apply
from two_layer_cover import half_blind_family, type_step
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT.parent / "depth-hand-proofs/verify"))
from sentinel_cegar import CNF, neg


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def holds(clauses, mask):
    return all(any(bool(mask >> (abs(lit) - 1) & 1) == (lit > 0)
                   for lit in clause) for clause in clauses)


def bit(mask, literal):
    return bool(mask >> (abs(literal) - 1) & 1) == (literal > 0)


def local_truth_tables():
    report = {}
    cnf = CNF()
    primary = [cnf.var() for _ in range(3)]
    output = cnf.conj(primary)
    for mask in range(1 << cnf.pool.top):
        assert holds(cnf.clauses, mask) == (bit(mask, output) == all(bit(mask, v) for v in primary))
    report["three_way_RR_indicator_assignments"] = 1 << cnf.pool.top
    cnf = CNF()
    lo, hi = cnf.var(), cnf.var()
    real = cnf.conj([lo, -hi])
    for mask in range(1 << cnf.pool.top):
        assert holds(cnf.clauses, mask) == (bit(mask, real) == (bit(mask, lo) and not bit(mask, hi)))
    report["real_marker_assignments"] = 1 << cnf.pool.top
    cnf = CNF()
    a, b, low, high, guard = [cnf.var() for _ in range(5)]
    cnf.gate(a, b, low, high, guard)
    for mask in range(1 << cnf.pool.top):
        expected = not bit(mask, guard) or (
            bit(mask, low) == (bit(mask, a) and bit(mask, b)) and
            bit(mask, high) == (bit(mask, a) or bit(mask, b)))
        assert holds(cnf.clauses, mask) == expected
    report["guarded_comparator_assignments"] = 1 << cnf.pool.top
    cnf = CNF()
    a, b, guard = [cnf.var() for _ in range(3)]
    cnf.eq(a, b, guard)
    for mask in range(1 << cnf.pool.top):
        assert holds(cnf.clauses, mask) == (not bit(mask, guard) or bit(mask, a) == bit(mask, b))
    report["guarded_idle_assignments"] = 1 << cnf.pool.top
    cnf = CNF()
    inputs = [cnf.var() for _ in range(3)]
    used = cnf.disj(inputs)
    for mask in range(1 << cnf.pool.top):
        assert holds(cnf.clauses, mask) == (bit(mask, used) == any(bit(mask, v) for v in inputs))
    report["used_indicator_assignments"] = 1 << cnf.pool.top
    return report


def cardinality_truth_tables():
    rows = []
    for n in (4, 5, 6):
        pool = IDPool()
        inputs = [pool.id() for _ in range(n)]
        cnf = CardEnc.atleast(inputs, 3, vpool=pool, encoding=EncType.seqcounter)
        accepted = set()
        for mask in range(1 << pool.top):
            if holds(cnf.clauses, mask):
                accepted.add(mask & ((1 << n) - 1))
        assert accepted == {m for m in range(1 << n) if m.bit_count() >= 3}
        rows.append({"input_count": n, "all_variable_assignments": 1 << pool.top,
                     "accepted_primary_assignments": len(accepted)})
    return rows


def transport_controls(cover):
    rows = []
    for case_index in (482, 603):
        case = cover[case_index]
        independent = states_of(case)
        encoded = [type_step(p, case["layers"][1])
                   for p in half_blind_family(17, case["layers"]).values()]
        assert set(independent) == set(encoded)
        assert all(s.count(0) == 9 for s in independent)
        matchings = [()]
        for shift in range(5):
            vertices = [(i + shift) % 17 for i in range(17)]
            matchings.append(tuple(tuple(sorted(vertices[i:i+2])) for i in range(0, 16, 2)))
        count = 0
        gates = 0
        for state in independent:
            free = [i for i, v in enumerate(state) if v == 0]
            for matching in matchings:
                after = apply(state, matching)
                bits = [(v >= 0, v >= 1) for v in state]
                nxt = bits[:]
                for a, b in matching:
                    nxt[a] = tuple(bits[a][q] and bits[b][q] for q in (0, 1))
                    nxt[b] = tuple(bits[a][q] or bits[b][q] for q in (0, 1))
                reals = [lo and not hi for lo, hi in nxt]
                assert [int(lo) + int(hi) - 1 for lo, hi in nxt] == after
                assert reals == [v == 0 for v in after] and sum(reals) == 9
                for second in matchings:
                    actual = sum(after[a] == after[b] == 0 for a, b in second)
                    indicators = sum((a, b) in second and reals[a] and reals[b]
                                     for a, b in itertools.combinations(range(17), 2))
                    assert indicators == actual
                    gates += 1
                for mask in range(512):
                    values = [-1 if v == -1 else 2 for v in state]
                    for j, wire in enumerate(free):
                        values[wire] = (mask >> j) & 1
                    result = apply(values, matching)
                    observed = [-1 if v == -1 else 1 if v == 2 else 0 for v in result]
                    assert observed == after
                    count += 1
        rows.append({"case": case_index, "independently_rebuilt_states": len(independent),
                     "signed_binary_transport_replays": count, "RR_count_controls": gates})
    return rows


def rebuild(source, case):
    spec = importlib.util.spec_from_file_location(f"review_build_{case}", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    captured = {}

    class StopBuild(Exception):
        pass

    class NoSolver:
        def __init__(self, **kwargs):
            captured["clauses"] = kwargs["bootstrap_with"]
            raise StopBuild

    module.Solver = NoSolver
    old = sys.argv
    try:
        with tempfile.TemporaryDirectory(prefix="d17-both-three-review-") as directory:
            destination = Path(directory) / "result.json"
            sys.argv = [str(source), "--case", str(case), "--out", str(destination)]
            try:
                module.main()
            except StopBuild:
                pass
            else:
                raise AssertionError("Solver interception failed")
            metadata = json.loads(destination.read_text())
    finally:
        sys.argv = old
    clauses = captured["clauses"]
    raw = (f'p cnf {metadata["variables"]} {len(clauses)}\n' +
           "".join(" ".join(map(str, c)) + " 0\n" for c in clauses)).encode()
    return metadata, raw


def bindings(source):
    rows = []
    for case in (482, 603):
        metadata, raw = rebuild(source, case)
        record = {"case": case, "variables": metadata["variables"],
                  "clauses": metadata["clauses"],
                  "rebuilt_cnf_sha256": hashlib.sha256(raw).hexdigest()}
        directory = ROOT / f"results/d17-both-three-recovery-case{case}"
        terminal = directory / "check-terminal.json"
        if not terminal.exists():
            record["certificate_status"] = "PENDING_TERMINAL_ARTIFACTS"
            rows.append(record)
            continue
        check = json.loads(terminal.read_text())
        result = json.loads((directory / "result.json").read_text())
        if not result.get("independently_proof_checked"):
            record["certificate_status"] = "PENDING_CHECK_MANIFEST"
            rows.append(record)
            continue
        assert result["status"] == "UNSAT" and result["iterations"] == 1
        assert result["source_sha256"] == sha(source)
        assert result["cover_sha256"] == sha(ROOT / "prefixes/complete17.jsonl")
        assert (directory / "result/problem.cnf").read_bytes() == raw
        assert result["cnf_sha256"] == record["rebuilt_cnf_sha256"]
        packed = directory / "result/proof.drat.gz"
        if packed.exists():
            assert result["proof_gzip_sha256"] == sha(packed)
            digest = hashlib.sha256()
            with gzip.open(packed, "rb") as stream:
                for block in iter(lambda: stream.read(1048576), b""):
                    digest.update(block)
            assert result["proof_sha256"] == digest.hexdigest()
        else:
            assert result["proof_sha256"] == sha(directory / "result/proof.drat")
        assert check["terminal"] and not check["timeout"] and check["returncode"] == 0
        assert "s VERIFIED" in (directory / "check.log").read_text()
        assert result["check_log_sha256"] == sha(directory / "check.log")
        assert result["checker_sha256"] == sha(Path(check["command"][0]))
        record.update({"certificate_status": "VERIFIED_BOUND",
                       "proof_sha256": result["proof_sha256"],
                       "check_log_sha256": result["check_log_sha256"],
                       "iterations": result["iterations"]})
        rows.append(record)
    return rows


def main():
    start = time.monotonic()
    source = ROOT / "d17_both_three_recovery_profile.py"
    cover_path = ROOT / "prefixes/complete17.jsonl"
    cover = [json.loads(line) for line in cover_path.read_text().splitlines()]
    result = {
        "mathematical_review": "ACCEPTED_NECESSARY_RELAXATION_FOR_COMPLETE_FIXED_PREFIX_CASES",
        "reviewed_implication": "A depth-nine sorter with the fixed two-layer cover prefix has an assignment satisfying this CNF after deleting immediately repeated later gates. Therefore checked UNSAT excludes all its continuations.",
        "necessary_premises": [
            "Every selected state is obtained by a genuine signed restriction blinding the fixed first two layers and leaving nine arbitrary real inputs.",
            "The first retained layer has at least three gates, by H9 plus the accepted N4 image rescheduling theorem.",
            "The second retained layer has at least three gates, by H9, N4 rescheduling, and the two checked UU/UD residuals.",
            "H9 forces at least one of the two retained layers to have four gates.",
            "Immediate repeated physical comparators can be deleted without changing the fixed prefix or the computed function."
        ],
        "source_review": [
            "Each physical later layer remains an arbitrary matching; no self-duality, co-saturation, or ending restriction is imposed.",
            "Two threshold bits propagate signed types exactly under a selected comparator; unused-wire identities are guarded by the exact used indicator.",
            "A second-edge indicator is exactly its physical gate AND its two transported real markers; the at-least-three cardinality counts retained gates.",
            "The peak selector encodes a necessary disjunction of first-four or second-four; at most one unmatched real among nine is equivalent to four RR gates.",
            "The legacy second-nonempty refinement branch is unreachable after the new min(profile)>=3 assertion and introduces no premise in first-iteration UNSAT."
        ],
        "local_truth_tables": local_truth_tables(),
        "cardinality_truth_tables": cardinality_truth_tables(),
        "transport_controls": transport_controls(cover),
        "certificate_bindings": bindings(source),
        "source_sha256": sha(source),
        "review_script_sha256": sha(Path(__file__)),
        "cover_sha256": sha(cover_path),
        "master_source_sha256": sha(ROOT.parent / "depth-hand-proofs/verify/sentinel_cegar.py"),
        "first_theorem_note_sha256": sha(ROOT / "d17_feedback_round10_order.md"),
        "second_theorem_note_sha256": sha(ROOT / "d17_second_recovery_order.md"),
        "second_theorem_check_sha256": sha(ROOT / "results/d17-second-recovery-check.json"),
        "new_SAT_calls": 0,
        "elapsed_seconds": time.monotonic() - start,
    }
    result["all_requested_certificates_bound"] = all(
        row["certificate_status"] == "VERIFIED_BOUND" for row in result["certificate_bindings"])
    destination = ROOT / "results/d17-both-three-recovery-review.json"
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
