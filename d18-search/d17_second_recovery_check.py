#!/usr/bin/env python3
"""Replay hand reductions and bind the two independently checked CNFs."""
import collections
import hashlib
import itertools
import json
import time
from pathlib import Path

import d17_second_recovery_exact as exact
import netsat
from height_two_recovery_review import matchings

ROOT = Path(__file__).parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def apply_real(layers, values):
    values = list(values)
    for layer in layers:
        for a, b in layer:
            values[a], values[b] = min(values[a], values[b]), max(values[a], values[b])
    return tuple(values)


def u_holds(y):
    return all(y[0] <= y[i] for i in (1, 2, 3)) and y[2] <= max(y[1], y[3])


def d_holds(z):
    return all(z[i] <= z[3] for i in (0, 1, 2)) and min(z[0], z[2]) <= z[1]


def u_inverse(y):
    return y if y[2] <= y[3] else (y[2], y[1], y[0], y[3])


def d_inverse(z):
    return z if z[0] <= z[1] else (z[0], z[3], z[2], z[1])


def images():
    report = {"domain_checks": 0, "inverse_checks": 0, "duality_checks": 0,
              "nine_wire_product_binary_checks": 0}
    for domain in (list(itertools.product(range(3), repeat=4)), list(itertools.permutations(range(4)))):
        for kind, last, holds, inverse in (("U", (0, 2), u_holds, u_inverse),
                                           ("D", (1, 3), d_holds, d_inverse)):
            prefix = [[(0, 1), (2, 3)], [last]]
            actual = {apply_real(prefix, x) for x in domain}
            expected = {x for x in domain if holds(x)}
            assert actual == expected, kind
            report["domain_checks"] += len(domain)
            for y in expected:
                assert apply_real(prefix, inverse(y)) == y
                report["inverse_checks"] += 1
        for y in domain:
            z = tuple(-v for v in reversed(y))
            assert u_holds(y) == d_holds(z)
            report["duality_checks"] += 1
    for kind, prefix in exact.PREFIXES.items():
        actual = netsat.prefix_images(9, prefix)
        expected = set()
        for mask in range(512):
            bits = tuple((mask >> i) & 1 for i in range(9))
            if u_holds(bits[:4]) and (u_holds if kind == "UU" else d_holds)(bits[4:8]):
                expected.add(mask)
            report["nine_wire_product_binary_checks"] += 1
        assert actual == expected and len(actual) == 128
    return report


def classification():
    first = ((0, 1), (2, 3), (4, 5), (6, 7))
    counts = collections.Counter()
    replays = 0
    rows = []
    for second in matchings(tuple(range(9))):
        if len(second) > 2:
            continue
        used = {v for e in second for v in e}
        free = [e for e in first if not (set(e) & used)]
        if len(second) <= 1:
            assert free
            kind = "at_most_one_second_gate"
        elif free:
            kind = "free_first_gate"
        else:
            assert len(second) == 2 and 8 not in used
            assert all(len(set(e) & used) == 1 for e in first)
            assert all(a // 2 != b // 2 for a, b in second)
            if any(a % 2 != b % 2 for a, b in second):
                kind = "opposite_role_rescheduling"
            else:
                kind = "".join(sorted("U" if a % 2 == 0 else "D" for a, b in second))
                if kind == "DU":
                    kind = "UD"
            rows.append({"second": second, "branch": kind})
        if free:
            gate = free[0]
            moved = [tuple(e for e in first if e != gate), second + (gate,)]
            assert len(moved[0]) == 3 and len(moved[1]) <= 3
            for x in range(512):
                assert netsat.apply_layers([first, second], x) == netsat.apply_layers(moved, x)
                replays += 1
        counts[kind] += 1
    assert dict(counts) == {"at_most_one_second_gate": 37, "free_first_gate": 330,
                            "opposite_role_rescheduling": 36, "UU": 3, "UD": 6, "DD": 3}
    return {"second_matchings": sum(counts.values()), "branches": dict(counts),
            "commutation_binary_replays": replays, "exceptional_path_rows": rows}


def certificate_binding():
    rows = []
    for case in exact.PREFIXES:
        out = ROOT / "results" / f"d17-second-recovery-{case.lower()}"
        result = json.loads((out / "result.json").read_text())
        assert result["status"] == "UNSAT_CHECKED" and result["independently_proof_checked"]
        assert result["source_sha256"] == sha(Path(exact.__file__))
        assert result["encoder_sha256"] == sha(Path(netsat.__file__))
        assert result["cnf_sha256"] == sha(out / "problem.cnf")
        assert result["proof_sha256"] == sha(out / "proof.drat")
        check = json.loads((out / "check-terminal.json").read_text())
        assert check["terminal"] and not check["timeout"] and check["returncode"] == 0
        assert "s VERIFIED" in (out / "check.log").read_text()
        checker = Path(check["command"][0])
        assert result["checker_binary_sha256"] == sha(checker)
        assert result["checker_source_sha256"] == sha(checker.parent / "drat-trim.c")
        assert result["checker_commit"] == exact.CHECKER_COMMIT
        model, universe = exact.build(case)
        try:
            encoded = exact.cnf_bytes(model)
            assert encoded == (out / "problem.cnf").read_bytes()
            assert len(universe) == result["unsorted_image_count"] == 118
            assert model.nv == result["variables"] and len(model.S.clauses) == result["clauses"]
        finally:
            model.S.delete()
        rows.append({"case": case, "cnf_rebuilt_identically": True,
                     "cnf_sha256": result["cnf_sha256"], "proof_sha256": result["proof_sha256"],
                     "check_log_sha256": sha(out / "check.log")})
    return rows


def main():
    started = time.monotonic()
    result = {"status": "VERIFIED", "scope": "Finite replay and certificate binding; universal reduction is in the accompanying hand proof. Full H9 and the established ending normal form remain premises.",
              "images": images(), "classification": classification(),
              "certificates": certificate_binding(),
              "source_sha256": sha(Path(__file__)),
              "note_sha256": sha(ROOT / "d17_second_recovery_order.md"),
              "elapsed_seconds": time.monotonic() - started}
    (ROOT / "results" / "d17-second-recovery-check.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "classification"}, indent=2))
    print(json.dumps({k: v for k, v in result["classification"].items() if k != "exceptional_path_rows"}, indent=2))


if __name__ == "__main__":
    main()
