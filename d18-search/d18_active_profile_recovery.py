#!/usr/bin/env python3
"""Bounded no-SAT raw-profile barrier and irredundant-profile investigation."""
import argparse
import collections
import gzip
import hashlib
import itertools
import json
import random
import time
from pathlib import Path

from two_layer_cover import half_blind_family, type_step
from restriction_budget_probe import irredundant_profile
from netsat import apply_layers, is_sorted

ROOT = Path(__file__).parent
SEED = 20261116


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def profile(net, placement):
    state = list(placement)
    result = []
    for layer in net:
        result.append(sum(state[a] == state[b] == 0 for a, b in layer))
        state = list(type_step(state, layer))
    return result


def violations(values):
    active = [v for v in values if v]
    result = []
    if len(active) < 7:
        result.append("depth")
    elif len(active) == 7:
        if max(active[:2]) < 4:
            result.append("H9_peak")
        if active[0] < 3:
            result.append("first_three")
        if active[1] < 3:
            result.append("second_three")
    return result


def build(seconds):
    start = time.monotonic()
    rng = random.Random(SEED)
    cover_path = ROOT / "prefixes/complete18.jsonl"
    cover = [json.loads(line) for line in cover_path.read_text().splitlines()]
    records = []
    for index, case in enumerate(cover):
        prefix = [[tuple(edge) for edge in layer] for layer in case["layers"]]
        states = {type_step(p, prefix[1]) for p in half_blind_family(18, prefix).values()}
        assert states and len(states) <= 64 and all(s.count(0) == 9 for s in states)
        layers = prefix[:]
        trials = []
        for _ in range(8):
            attempts = 0
            previous = set(layers[-1])
            while True:
                if time.monotonic() - start > seconds:
                    raise TimeoutError("Bounded witness construction stopped")
                attempts += 1
                vertices = list(range(18))
                rng.shuffle(vertices)
                layer = sorted(tuple(sorted(vertices[i:i+2])) for i in range(0, 18, 2))
                if previous.intersection(layer):
                    continue
                if all(any(state[a] == state[b] == 0 for a, b in layer) for state in states):
                    break
            layers.append(layer)
            trials.append(attempts)
            states = {type_step(state, layer) for state in states}
        failure = None
        for _ in range(128):
            mask = rng.randrange(1 << 18)
            output = apply_layers(layers, mask)
            if not is_sorted(output, 18):
                failure = {"input": mask, "output": output}
                break
        assert failure is not None
        records.append({"case": index, "case_id": case["case_id"],
                        "suffix": layers[2:], "attempts_per_layer": trials,
                        "binary_sorting_failure": failure})
    report = {"status": "CONSTRUCTED_ALL_411_RAW_RELAXATION_WITNESSES",
              "scope": "Every original first-two-blind nine-real state remains raw-active in each of eight later layers. These networks are explicitly nonsorting; no complete case is excluded or solved.",
              "seed": SEED, "source_sha256": sha(Path(__file__)),
              "cover_sha256": sha(cover_path), "records": records,
              "elapsed_seconds": time.monotonic() - start}
    path = ROOT / "results/d18-active-profile-recovery-witnesses.json.gz"
    path.write_bytes(gzip.compress((json.dumps(report, separators=(",", ":")) + "\n").encode(), mtime=0))
    print(json.dumps({"records": len(records), "seconds": report["elapsed_seconds"],
                      "maximum_matching_attempts": max(max(r["attempts_per_layer"]) for r in records),
                      "compressed_bytes": path.stat().st_size}))


def direct_irredundant(net, placement):
    """Independent scalar512-input replay; sentinels are actual -1/+2."""
    free = [i for i, v in enumerate(placement) if v == 0]
    assert len(free) == 9
    swaps = [set() for _ in net]
    raw = profile(net, placement)
    for mask in range(512):
        values = [-1 if v == -1 else 2 for v in placement]
        for j, wire in enumerate(free):
            values[wire] = (mask >> j) & 1
        types = list(placement)
        for t, layer in enumerate(net):
            for a, b in layer:
                if types[a] == types[b] == 0 and values[a] > values[b]:
                    swaps[t].add((a, b))
                values[a], values[b] = min(values[a], values[b]), max(values[a], values[b])
                types[a], types[b] = min(types[a], types[b]), max(types[a], types[b])
    return raw, [len(row) for row in swaps]


def check(seconds):
    start = time.monotonic()
    witness_path = ROOT / "results/d18-active-profile-recovery-witnesses.json.gz"
    saved = json.loads(gzip.decompress(witness_path.read_bytes()))
    cover_path = ROOT / "prefixes/complete18.jsonl"
    cover = [json.loads(line) for line in cover_path.read_text().splitlines()]
    assert saved["cover_sha256"] == sha(cover_path)
    assert saved["source_sha256"] == sha(Path(__file__))
    assert [r["case"] for r in saved["records"]] == list(range(411))
    profile_counts = collections.Counter()
    raw_states = 0
    case_rows = []
    examples = {}
    direct_examples = []
    for row in saved["records"]:
        if time.monotonic() - start > seconds:
            raise TimeoutError("Bounded irredundant audit stopped")
        case = cover[row["case"]]
        net = [[tuple(edge) for edge in layer] for layer in case["layers"] + row["suffix"]]
        assert len(net) == 10
        for t, layer in enumerate(net):
            used = [v for edge in layer for v in edge]
            assert len(used) == len(set(used)) and all(0 <= a < b < 18 for a, b in layer)
            if t:
                assert not set(layer).intersection(net[t-1])
            if t >= 2:
                assert len(layer) == 9
        failure = row["binary_sorting_failure"]
        assert apply_layers(net, failure["input"]) == failure["output"]
        assert not is_sorted(failure["output"], 18)
        failures = collections.Counter()
        old_reject = new_reject = False
        for placement in half_blind_family(18, case["layers"]).values():
            exact = irredundant_profile(net, list(placement))
            raw = exact["raw_profile"]
            assert raw == profile(net, placement) and raw[:2] == [0, 0] and all(raw[2:])
            retained = exact["irredundant_profile"]
            active = [v for v in retained if v]
            profile_counts[len(active)] += 1
            raw_states += 1
            bad = violations(retained)
            old = any(v in ("depth", "H9_peak") for v in bad)
            new = bool(bad)
            old_reject |= old
            new_reject |= new
            for reason in bad:
                failures[reason] += 1
                if reason not in examples:
                    example = {"case": row["case"], "placement": placement, **exact,
                               "active_irredundant_profile": active, "violations": bad}
                    examples[reason] = example
                    direct_examples.append((net, example))
            if new and not old and "new_only" not in examples:
                example = {"case": row["case"], "placement": placement, **exact,
                           "active_irredundant_profile": active, "violations": bad}
                examples["new_only"] = example
                direct_examples.append((net, example))
        case_rows.append({"case": row["case"], "old_irredundant_screen_rejects": old_reject,
                          "new_irredundant_screen_rejects": new_reject,
                          "old_passes_but_new_rejects": new_reject and not old_reject,
                          "restriction_violation_counts": dict(failures)})
    budget_path = ROOT / "results/budget-counterexample18.json"
    budget = json.loads(budget_path.read_text())
    budget_net = [[tuple(edge) for edge in layer] for layer in budget["network"]]
    rng = random.Random(SEED + 1)
    budget_states = {tuple(p) for p in half_blind_family(18, budget_net[:2]).values()}
    budget_states.add(tuple(budget["nine_real_audit"]["minimum_witness"]))
    for _ in range(5000):
        free = set(rng.sample(range(18), 9))
        state = [0 if i in free else rng.choice((-1, 1)) for i in range(18)]
        budget_states.add(type_step(state, budget_net[0]))
    budget_hist = collections.Counter()
    budget_bad = collections.Counter()
    budget_examples = {}
    for state in sorted(budget_states):
        if time.monotonic() - start > seconds:
            raise TimeoutError("Bounded budget-witness sample stopped")
        exact = irredundant_profile(budget_net, list(state))
        assert len([v for v in exact["raw_profile"] if v]) >= 8
        active = [v for v in exact["irredundant_profile"] if v]
        budget_hist[len(active)] += 1
        bad = violations(exact["irredundant_profile"])
        for reason in bad:
            budget_bad[reason] += 1
            if reason not in budget_examples:
                example = {"placement": state, **exact,
                           "active_irredundant_profile": active, "violations": bad}
                budget_examples[reason] = example
                direct_examples.append((budget_net, example))
        if bad and not any(v in ("depth", "H9_peak") for v in bad) and "new_only" not in budget_examples:
            example = {"placement": state, **exact,
                       "active_irredundant_profile": active, "violations": bad}
            budget_examples["new_only"] = example
            direct_examples.append((budget_net, example))
    seen_direct = set()
    for net, example in direct_examples:
        key = json.dumps([net, example["placement"]])
        if key in seen_direct:
            continue
        seen_direct.add(key)
        raw, retained = direct_irredundant(net, example["placement"])
        assert raw == example["raw_profile"] and retained == example["irredundant_profile"]
    report = {
        "status": "VERIFIED_RAW_WITNESSES_AND_IRREDUNDANT_AUDIT",
        "scope": "All411 witness networks are checked only against their first-two-blind nine-real families. Rejection concerns these specific constructed networks, not whole cover cases. The separate budget-network sample is not exhaustive.",
        "raw_witness_cases": len(case_rows), "raw_signed_restrictions_checked": raw_states,
        "all_raw_profiles_have_eight_active_layers": True,
        "all_witnesses_have_no_immediate_repeated_gate": True,
        "all_witnesses_explicitly_nonsorting": True,
        "irredundant_active_layer_histogram": dict(profile_counts),
        "old_irredundant_screen_rejected_networks": sum(r["old_irredundant_screen_rejects"] for r in case_rows),
        "new_irredundant_screen_rejected_networks": sum(r["new_irredundant_screen_rejects"] for r in case_rows),
        "old_pass_new_fail_cases": [r["case"] for r in case_rows if r["old_passes_but_new_rejects"]],
        "representative_restrictions": examples, "cases": case_rows,
        "budget_network_sample": {"source_sha256": sha(budget_path),
                                  "sampled_states": len(budget_states),
                                  "irredundant_active_layer_histogram": dict(budget_hist),
                                  "violation_counts": dict(budget_bad),
                                  "representative_restrictions": budget_examples},
        "independent_scalar_binary_replays": 512 * len(seen_direct),
        "source_sha256": sha(Path(__file__)), "cover_sha256": sha(cover_path),
        "witness_sha256": sha(witness_path),
        "irredundancy_source_sha256": sha(ROOT / "restriction_budget_probe.py"),
        "new_SAT_calls": 0, "elapsed_seconds": time.monotonic() - start,
    }
    destination = ROOT / "results/d18-active-profile-recovery-check.json"
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("cases", "representative_restrictions", "budget_network_sample")}, indent=2))
    print(json.dumps({"budget_network_sample": {k: v for k, v in report["budget_network_sample"].items() if k != "representative_restrictions"}}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("build", "check"))
    parser.add_argument("--seconds", type=float, default=30)
    args = parser.parse_args()
    (build if args.mode == "build" else check)(args.seconds)


if __name__ == "__main__":
    main()
