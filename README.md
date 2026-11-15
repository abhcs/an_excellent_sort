# an_excellent_sort

## Integrated Mathathon submission

The current synthesis is in [mathathon-submission](mathathon-submission/README.md):

- [32-page report](mathathon-submission/report.pdf) and [self-contained LaTeX source](mathathon-submission/report.tex)
- [20-slide presentation](mathathon-submission/slides.pdf) and [editable PowerPoint](mathathon-submission/slides.pptx)
- [Machine-readable claim ledger](mathathon-submission/supplementary/claim-ledger.json) with dependencies, source hashes, verification commands, and limits
- [Lean source, formal statement mapping, and build instructions](mathathon-submission/supplementary/lean/README.md)
- [Reproduction and collaborator-integration instructions](mathathon-submission/HANDOFF.md)

The report emphasizes the completed hand arguments through ten wires, structural results mined from SAT-guided exploration, concrete constructions, and the remaining open work. Both Lean checks passed for two-layer removal and the halving recurrence. We plan to formalize all of the work. The forthcoming open-model AKS derivation remains pending. The original collaborator files at the repository root are retained as source material; the integrated report above is the current synthesis.

A sandbox for exploring **sorting networks**: fixed sequences of
compare-and-swap operations that sort every possible input.

## Sorting networks in brief

A sorting network on *n* wires is a list of comparators `(i, j)` with `i < j`.
Each comparator compares the values on wires `i` and `j` and swaps them if
needed, so the smaller value ends up on wire `i`. The sequence of comparisons
never depends on the data, which suits hardware, SIMD and GPUs, and code that
must run in constant time.

This network sorts 4 inputs with 5 comparators in 3 layers. Each vertical line
is a comparator, and `+` marks a line passing over a wire it doesn't touch:

```text
0 --o---o-----------
    |   |
1 --o---+--o---o----
        |  |   |
2 --o---o--+---o----
    |      |
3 --o------o--------
```

In the layer notation used by Dobbelaere's list (see References):
`[(0,1),(2,3)] [(0,2),(1,3)] [(1,2)]`.

Two numbers measure a network:

- **size**: the number of comparators
- **depth**: the number of parallel layers, where the comparators in one layer
  touch disjoint wires

**The 0-1 principle.** A network sorts every input if and only if it sorts all
2ⁿ inputs made of 0s and 1s, so checking a network takes 2ⁿ tests instead of n!.

## Known bounds

Best known values as of November 2026, from Dobbelaere's list. Every depth
below is proven optimal. Sizes are proven optimal up to n = 12; beyond that,
`44–45` means the minimum is at least 44 and a 45-comparator network exists.

| n  | depth | size  |
|---:|------:|------:|
| 1  | 0     | 0     |
| 2  | 1     | 1     |
| 3  | 3     | 3     |
| 4  | 3     | 5     |
| 5  | 5     | 9     |
| 6  | 5     | 12    |
| 7  | 6     | 16    |
| 8  | 6     | 19    |
| 9  | 7     | 25    |
| 10 | 7     | 29    |
| 11 | 8     | 35    |
| 12 | 8     | 39    |
| 13 | 9     | 44–45 |
| 14 | 9     | 48–51 |
| 15 | 9     | 53–56 |
| 16 | 9     | 57–60 |
| 17 | 10    | 63–71 |

The size lower bounds for n ≥ 13 were tightened in April 2025. Older sources,
including Wikipedia as of November 2026, still give 43, 47, 51, 55 and 60.

Size and depth can't always both be optimal: on 10 wires, 29 comparators need
8 layers, and any 7-layer network needs at least 31.

## Things to explore

- **Verification**: run the 0-1 test bit-parallel. Store wire k as a 2ⁿ-bit
  integer holding its value on every 0-1 input. A comparator then maps
  `(a, b)` to `(a & b, a | b)`, and the network sorts if and only if
  `w[k] & ~w[k+1] == 0` for every k.
- **Constructions**: Batcher's odd-even merge sort and bitonic sorter, the
  pairwise network, insertion and bubble networks. How far are they from the
  table?
- **Search**: hunt for small or shallow networks with evolutionary search over
  a fixed prefix (as SorterHunter does), SAT encodings, or generate-and-prune.
- **Pictures**: draw networks as Knuth diagrams like the one above.
- **Speed**: benchmark branchless and SIMD networks against a library sort on
  small arrays.

## References

- D. E. Knuth, *The Art of Computer Programming, Vol. 3: Sorting and
  Searching*, 2nd ed., Addison-Wesley, 1998, §5.3.4.
- K. E. Batcher, "Sorting networks and their applications", AFIPS Spring Joint
  Computer Conference, 1968.
- D. Bundala and J. Závodný, "Optimal sorting networks", LATA 2014. Optimal
  depth for 11 ≤ n ≤ 16.
- M. Codish, L. Cruz-Filipe, M. Frank and P. Schneider-Kamp, "Sorting nine
  inputs requires twenty-five comparisons", *Journal of Computer and System
  Sciences* 82(3), 2016. Optimal size for n = 9 and 10.
- M. Codish, L. Cruz-Filipe, T. Ehlers, M. Müller and P. Schneider-Kamp,
  "Sorting networks: to the end and back again", *Journal of Computer and
  System Sciences*, 2016. Optimal depth for n = 17.
- J. Harder, "An answer to the Bose-Nelson sorting problem for 11 and 12
  channels", 2020, [arXiv:2012.04400](https://arxiv.org/abs/2012.04400); code at
  [jix/sortnetopt](https://github.com/jix/sortnetopt). Optimal size for n = 11
  and 12.
- J. A. R. Fonollosa, "Joint size and depth optimization of sorting networks",
  2018. Size–depth trade-offs such as the one for n = 10.
- B. Dobbelaere, [smallest and fastest sorting networks](https://bertdobbelaere.github.io/sorting_networks.html)
  for up to 32 inputs, with an
  [extended list](https://bertdobbelaere.github.io/sorting_networks_extended.html)
  for larger n. Many were found with
  [SorterHunter](https://github.com/bertdobbelaere/SorterHunter).
- OEIS [A003075](https://oeis.org/A003075) (minimal size) and
  [A067782](https://oeis.org/A067782) (minimal depth).
- Wikipedia, [Sorting network](https://en.wikipedia.org/wiki/Sorting_network).
