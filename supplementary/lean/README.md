# SortingDepth — Lean verification report

Lean code was produced in following session.
https://chatgpt.com/share/6af93395-07dc-83e8-9ad3-8c3919420900


## Reproduce from this repository


```bash
# Required verification build.
lake build

# Recheck the source and print the transitive axioms of both main theorems.
lake env lean SortingDepth.lean
```

Expected final compiler output:

```text
'SortingDepth.remove_two_layers' depends on axioms: [propext, Classical.choice, Quot.sound]
'SortingDepth.D_ceil_half_add_two' depends on axioms: [propext, Classical.choice, Quot.sound]
```

## Mathematical claims and declaration correspondence

### Wire and network semantics

| Lean declaration | Claim or meaning assigned in the report | Difference / qualification |
|---|---|---|
| `SortingDepth.Layer` | A layer is an involution `mate` on wires. On `Fin n`, its two-element orbits are disjoint comparators and its fixed points are idle wires. | This is an abstract involution representation, not a list of comparator pairs. Finiteness is used only for the `Fin n` results. |
| `SortingDepth.Layer.run` | A comparator sends the minimum to the smaller wire index and the maximum to the larger; an idle wire is unchanged. | The wire order is the given `LinearOrder`; no comparability with values is required beyond its own `LinearOrder`. |
| `SortingDepth.run` | Executes a list of layers from head to tail. | It is a function on wire-indexed value functions, not an executable array algorithm. |
| `SortingDepth.Sorts` | A network sorts every Boolean input into nondecreasing wire order. | The definition itself quantifies only over `Bool`; `SortingDepth.Sorts.mono_run` proves the extension to every linearly ordered value type (the zero-one principle). |
| `SortingDepth.D` | The least list length among networks on `Fin n` satisfying `Sorts`. | `D` is noncomputable and is defined with `Nat.find`; the file proves an inequality about it, not an algorithm or closed formula for evaluating it. |

For natural-number division, `(n + 1) / 2` is exactly $\lceil n/2\rceil$. Monotonicity means nondecreasing order, not strict monotonicity.

### Main results

#### `SortingDepth.remove_two_layers`

```lean
theorem remove_two_layers {n : ℕ} (A B : Layer (Fin n)) (N : List (Layer (Fin n)))
    (hs : Sorts (A :: B :: N)) :
    ∃ M : List (Layer (Fin ((n + 1) / 2))), Sorts M ∧ M.length = N.length
```

**Report claim.** From any sorting network with a syntactic two-layer prefix, one can construct a sorting network on $\lceil n/2\rceil$ wires using exactly the remaining number of layers.

**Difference / qualification.** This is an existential pruning construction, not a claim that the output is a literal subnetwork of the input. It does not itself compare optimal depths and needs no separate hypothesis `3 ≤ n`. The proof may fill idle positions in the first layer, two-colour alternating components, relabel live wires, and reduce the remaining layers.

#### `SortingDepth.D_ceil_half_add_two`

```lean
theorem D_ceil_half_add_two (n : ℕ) (hn : 3 ≤ n) : D ((n + 1) / 2) + 2 ≤ D n
```

**Report claim.** For $n\ge3$, minimum sorting-network depth obeys
$D(\lceil n/2\rceil)+2\le D(n)$.

**Difference / qualification.** This is a one-sided lower-bound recurrence, not an equality, a converse bound, a closed-form depth, or a computation of any concrete optimal depth. The assumption $n\ge3$ ensures that every sorter has at least two layers, allowing removal of the first two layers from a minimum-length witness.

### Public supporting declarations

| Declaration | Claim it supports | Difference / qualification |
|---|---|---|
| `SortingDepth.Sorts.mono_run` | Extends Boolean sorting to monotonic output on every linearly ordered value type. | Uses the zero-one principle; it does not claim that each individual comparator is monotone in both inputs. |
| `SortingDepth.Layer.Full` | Defines a full layer as having at most one idle wire. | “Full” permits one fixed point, as required on an odd number of wires. |
| `SortingDepth.exists_full_first` | Replaces the first layer by a full one while preserving sorting and the tail. | The replacement can add comparators; no uniqueness is claimed. |
| `SortingDepth.two_colour` | Produces the alternating Boolean live/dead colouring used by pruning, with idle first-layer wires live. | This is an existence theorem for a colouring, not an explicit efficient colouring algorithm. |
| `SortingDepth.two_le_length` | Every sorter on at least three wires has at least two layers. | It is only a lower bound of two, not an optimal-depth estimate by itself. |
| `SortingDepth.sorter_exists` | A sorting network exists on every finite wire type `Fin n`. | The recursive construction is for existence and well-definedness of `D`; it is not claimed to be depth-optimal. |
| `SortingDepth.D_le_length` | `D n` is at most the length of any sorter on `Fin n`. | This is the minimisation direction used after pruning; the main proof also uses `Nat.find_spec` to choose a minimum witness. |

### Source-level internal declarations used transitively

The following table inventories the remaining declarations used by the reported proofs. These are internal proof steps or representation definitions, **not additional report-level mathematical claims**; accordingly, there is no separate external-claim discrepancy for them. Source-declared `private` names are written as they appear in the file rather than with Lean's generated private-name prefix.

| Declarations | Supporting role |
|---|---|
| `Layer.mate_mate`, `Layer.perm`, `Layer.relabel`, `Layer.restrict`, `Layer.run_of_fixed`, `Layer.run_of_monotone`, `Layer.run_mono_of_monotone`, `Layer.switch`, `Layer.run_switch`, `Layer.run_eq_switch`, `Layer.switch_eq_self_iff`, `Layer.switch_comm` | Involution laws, layer restriction/relabeling, execution laws, and the input-permutation switch used throughout the reduction. |
| `run_append`, `run_monotone_map`, `run_of_monotone`, `exists_input_perm` | Network concatenation, monotone maps (for the zero-one principle), sorted-input invariance, and permutation of input values. |
| `fixed` (private), `fillPair` (private), `onlyPair` (private), `fillPair_run` (private) | Decrease the number of idle wires while preserving sorting in `exists_full_first`. |
| `Walk` (private), `Walk.snoc` (private), `Walk.reverse` (private), `Walk.append` (private), `next` (private), `Alt` (private), `Alt.succ_iff` (private), `Alt.zero_eq` (private), `next_next` (private), `no_alt_odd` (private), `Alt.toWalk` (private), `Walk.alt_or_shorter` (private), `Walk.closed_even` (private) | Alternating-walk infrastructure and the parity argument behind `two_colour`. |
| `Tag`, `mid`, `high`, `Box`, `value`, `encode`, `tag_cases`, `mid_ne_bot`, `high_ne_bot`, `high_ne_mid`, `value_strictMono`, `encode_mid`, `encode_lt`, `encode_same` (all private) | Three-tag reference encoding and its strict-order properties for pruning. |
| `Labels`, `embed`, `embed_injective`, `pack`, `pack_live`, `pack_encode`, `cut`, `cut_mate_of_live`, `cut_mate_of_dead`, `tagLabels`, `advance`, `advance_embed`, `run_encoded_of_not_both_live`, `Layer.run_pack` (all private) | Relate a reference run to the reduced network while tracking live-wire labels and comparator orientation. |
| `finalLabels`, `reduced`, `reduced_length`, `run_pack`, `reduced_sorts`, `cut_run_eq_self`, `mask`, `mask_is_mid`, `mask_fixed`, `mask_no_comparator`, `card_live` (all private) | Iterate the reduction, preserve sorting and length, make the first two reduced layers identities, and count exactly $\lceil n/2\rceil$ live wires. |
| `onlyOne`, `mono_onlyOne`, `run_onlyOne` (all private) | Single-true-bit inputs used to prove `two_le_length`. |
| `castLower`, `castLower_run`, `run_castLower`, `run_castLower_last`, `maxPrefix`, `maxPrefix_last` (all private) | Inductive sorter construction behind `sorter_exists`. |
| `HasDepth`, `exists_depth` (both private) | Depth-witness predicate and existence used to define `D` with `Nat.find`. |

No other project theorem is assigned a claim in this report. Mathlib declarations retain their own meanings and are checked through the pinned dependency revision rather than re-reported as project results.

## Dependency pins

`lakefile.toml` pins Mathlib by the full v4.35.0 commit, and `lake-manifest.json` pins the complete transitive dependency set. The generated lockfile is part of the ZIP; it, not a moving branch name, is authoritative for reproducibility.

| Package | Locked commit |
|---|---|
| `mathlib` (v4.35.0) | `56a005855ea17e0b0958f73ec801ae140b0a1679` |
| `plausible` | `dfa4f38190d07c37e315953e08b90fe2d95b3c24` |
| `LeanSearchClient` | `d6b4c7be5be75ec4917c873ac50c756dc1436372` |
| `importGraph` | `a41f0e9a4dea23188ea9cc1c41ac9f8bbafe0b93` |
| `proofwidgets` | `df72b022e558978a1c50264cfc4d7fec86fa8e04` |
| `aesop` | `4a174c490d8707121c4a9290800489f105d85e07` |
| `Qq` | `dce0ad79c486cb1fb504af04f953c3466b0c6db8` |
| `batteries` | `66e469188fe07963e5cf666c7d4433f45b8131c5` |
| `Cli` | `c24fe6078c630e89b489bffe59b3e20ac30d12c8` |

