#!/usr/bin/env python3
"""Census compatible height-two prefixes; no cover exclusions are claimed."""
import collections
import hashlib
import json
import time
from pathlib import Path

from height_two_recovery_review import transform

ROOT = Path(__file__).parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def structure(n, edges):
    outgoing = collections.defaultdict(list)
    graph = [set() for _ in range(n)]
    for a, b in edges:
        outgoing[a].append(b)
        graph[a].add(b)
        graph[b].add(a)
    matched = {}

    def augment(a, seen):
        for b in outgoing[a]:
            if b in seen:
                continue
            seen.add(b)
            if b not in matched or augment(matched[b], seen):
                matched[b] = a
                return True
        return False

    for a in sorted(outgoing):
        augment(a, set())
    remaining = set(range(n))
    components = []
    while remaining:
        stack = [min(remaining)]
        seen = set()
        while stack:
            v = stack.pop()
            if v in seen:
                continue
            seen.add(v)
            stack.extend(graph[v] - seen)
        remaining -= seen
        components.append(sorted(seen))
    return {
        "width": n - len(matched),
        "width_method": "n minus maximum bipartite matching in height-two relation graph",
        "maximum_matching": sorted((a, b) for b, a in matched.items()),
        "component_count": len(components),
        "component_sizes": sorted(map(len, components)),
        "relations": sorted(edges),
    }


def inspect(n, layers):
    edges = ()
    for number, layer in enumerate(layers, 1):
        result = transform(n, edges, tuple(tuple(g) for g in layer))
        if result is None:
            return {"compatible": False, "first_incompatible_layer": number}
        _, edges = result
    return {"compatible": True, "layers_checked": len(layers), **structure(n, edges)}


def main():
    start = time.monotonic()
    covers = []
    for n in (18, 17):
        path = ROOT / "prefixes" / f"complete{n}.jsonl"
        raw = [json.loads(line) for line in path.read_text().splitlines()]
        accepted = []
        failed = collections.Counter()
        for index, record in enumerate(raw):
            assert record["n"] == n and len(record["layers"]) == 2
            row = inspect(n, record["layers"])
            if row["compatible"]:
                accepted.append({"index": index, "case_id": record["case_id"], **row})
            else:
                failed[row["first_incompatible_layer"]] += 1
        covers.append({
            "n": n, "source": str(path.relative_to(ROOT)), "source_sha256": digest(path),
            "cover_count": len(raw), "compatible_count": len(accepted),
            "compatible_indices": [r["index"] for r in accepted],
            "incompatible_layer_counts": dict(failed),
            "component_count_distribution": dict(collections.Counter(r["component_count"] for r in accepted)),
            "width_distribution": dict(collections.Counter(r["width"] for r in accepted)),
            "compatible_cases": accepted,
        })
    sampled_path = ROOT / "results" / "rank-layer-round6-hand-certificate.json"
    sampled = json.loads(sampled_path.read_text())
    samples = []
    for record in sampled["records"]:
        for depth in (4, 5, 6):
            assert len(record["prefix"]) >= depth
            layers = record["prefix"][:depth]
            samples.append({"name": record["name"], "prefix_depth": depth,
                            **inspect(18, layers)})
    report = {
        "status": "VERIFIED_CENSUS",
        "scope": "These are compatible-prefix recognitions, not complete-cover exclusions. Failure of this sufficient invariant does not rule out another poset-image representation or a signed restriction.",
        "covers": covers,
        "sampled_prefix_source": str(sampled_path.relative_to(ROOT)),
        "sampled_prefix_source_sha256": digest(sampled_path),
        "sampled_prefixes": samples,
        "source_sha256": digest(Path(__file__)),
        "transform_source_sha256": digest(ROOT / "height_two_recovery_review.py"),
        "elapsed_seconds": time.monotonic() - start,
    }
    destination = ROOT / "results" / "height-two-cover-recovery-census.json"
    with destination.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"covers": [{k: r[k] for k in ("n", "cover_count", "compatible_count", "compatible_indices", "component_count_distribution", "width_distribution")} for r in covers],
                      "sampled_prefixes": samples, "elapsed_seconds": report["elapsed_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
