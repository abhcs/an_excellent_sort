# SortingNetworks project: all results and proofs (handoff report)

Date: 2026-11-15. Compiled from the 30 project notes (`claude/*.md`), the 17 project chats, and checks run while writing this report. It is meant to be read by another Claude instance with no other context.

## 0. How to read this

**Goal of the project.** Understand O(log n)-depth sorting networks better: simpler proofs, smaller constants, fixed-n records, lower bounds.

**Status tags** (every result carries one):
- **PROVED**: a complete proof is written in this report. Hand proofs, not machine-checked.
- **EXACT**: established by exhaustive computation on the stated finite class.
- **LIT**: taken from the literature, usually read through a web summariser, not re-derived.
- **AGENT**: reported by a sub-agent in an earlier session; proof or code no longer available; not reviewed.
- **SIM**: simulation or adversarial search; evidence only.
- **RETRACTED / FLAWED**: known to be wrong or to have a gap; kept so that nobody re-derives it by accident.

**What is not available.** Almost all code and agent write-ups lived in session scratch directories and are gone. Surviving artefacts: the project notes, and for section 4 the files `net_1024.json`, `verify.py` (sent in chat; code reproduced in the appendix so everything can be regenerated).

**Two things found while writing this report** (not in the earlier notes):
1. The "weight recursion" used in note L1 to reconstruct the 3.27 log2 n lower bound is false as stated (4-wire counterexample, section 3.2). A correct potential inequality is proved here instead; it gives Yao's 2.41 log2 n and a 3 log2 n bound, not 3.27.
2. The proof of "last-layer comparators are adjacent" written in note P2 has a gap (section 2.8). The statement is a published result and holds exhaustively for n = 4, 5.

**Conventions.** Wires 0..n-1. A standard comparator (a,b), a < b, puts the min on a and the max on b. A layer is a set of disjoint comparators; depth = number of layers. D(n) = minimum depth of a sorting network on n wires. M(r) = the largest n with D(n) <= r; known values M(0..9) = 1, 2, 2, 4, 4, 6, 8, 10, 12, 16 (LIT: D(n) for n <= 17 is 0,1,3,3,5,5,6,6,7,7,8,8,9,9,9,9,10). L = log2 n. "Sorted" = nondecreasing in wire order. In 0-1 inputs with w ones the sorted output is 0^(n-w) 1^w.

---

## 1. Basic tools

**1.1 Zero-one principle (LIT, standard).** A comparator network sorts all inputs iff it sorts all 0-1 inputs. Same for merging networks restricted to sorted-block 0-1 inputs.

**1.2 Monotonicity (PROVED).** A comparator network is a monotone map on 0-1 vectors: x <= y coordinatewise implies N(x) <= N(y). Proof: min and max are monotone. QED

**1.3 Prefix monotonicity (PROVED; "F1"/"L1" in the notes).** For a standard network and any cut c, the number of ones on wires < c never increases. Proof: a standard comparator leaves a 0-1 vector unchanged or moves a one from a to b > a. QED

**1.4 Untangling (PROVED; Knuth 5.3.4 ex. 16).** A *generalized* comparator (p,q) puts min on p and max on q for arbitrary p != q. If a generalized network N sorts every input, there is a standard network N' with the same number of comparators in the same layers that sorts every input.
Proof. Process comparators in order, keeping a relabeling pi of wires (initially the identity). For a generalized comparator (p,q) let p' = pi(p), q' = pi(q). If p' < q' emit (p',q'). Otherwise emit (q',p') and compose pi with the transposition of p' and q' (the two wires now hold each other's contents relative to N, so every later reference is exchanged). The result N' is standard, and there is a fixed permutation sigma of wires with N'(x) = sigma(N(x)) for all x. A standard network leaves the sorted input (0,1,..,n-1) unchanged, and N maps it to the same sorted sequence, so sigma is the identity. Hence N' sorts. Layers stay layers because relabeling is a bijection. QED
Consequence (chat "Directed comparators"): allowing arbitrarily directed comparators cannot change the optimal depth or size of sorters, halvers, mergers or selectors. Direction matters only when later layers or the topology are fixed.

**1.5 Monotonicity of D (PROVED).** D(m) <= D(h) for m <= h. Proof: in a standard h-sorter put +infinity on the top h-m wires; a +infinity on a top wire is always the max of its comparator and stays. Delete those wires and their comparators. QED

**1.6 Cones (PROVED).** After t layers each wire depends on at most 2^t inputs; a wire s layers before the end reaches at most 2^s outputs. Proof: each comparator at most doubles. QED

**1.7 Forcing sets (PROVED; "L6").** For every wire v and time t there is a set S(v,t) of at most 2^t input wires such that every 0-1 input with ones on S(v,t) has a one on v after t layers. In a standard network S(v,t) can be chosen inside [v, n).
Proof. S(v,0) = {v}. At a comparator (a,b): S(a,t+1) = S(a,t) u S(b,t) (min is AND), S(b,t+1) = S(b,t) (max is OR). Sizes at most double; "all >= v" is preserved because b > a. QED
(For the max output one may instead take the smaller of the two sets; then the location property is lost. This is the "min-support adversary".)

**1.8 Minterm criterion (PROVED; "L7").** A standard network sorts iff for every output wire i, every 0-1 input producing a one on output i has weight >= n - i. So a forcing set of output i with fewer than n - i elements is an unsorted input. Proof: a sorted output with a one at i has ones on i..n-1; conversely if the output of x is unsorted with leftmost one at i then i < n - |x|. QED

---

## 2. Depth lower bounds for fixed n

### 2.1 Halving lemma (PROVED): D(n) >= D(ceil(n/2)) + 2 for n >= 3

Proof. Let N be a standard sorter on n >= 3 wires of depth d (d >= 2), with first two layers F and L. The graph F u L on the wires is a union of two matchings, so it consists of paths and even cycles (a comparator repeated in both layers is a 2-cycle) and is bipartite. Two-colour it and let C be a colour class with |C| <= floor(n/2); V = the other wires, h = |V| >= ceil(n/2).
Inputs: arbitrary distinct real values ("variables") on V; constants on C chosen so that they do not move in layer 1: if c in C is the min-wire of its F-comparator put -infinity on it, if it is the max-wire put +infinity, if it is idle in F put either. Every comparator of F and L joins C to V, so in layers 1 and 2 no two variables are compared, and after layer 1 the constants are still on C and the variables on V.
Tokens. When a variable meets a constant at any comparator, the outcome does not depend on the variable's value (-infinity always takes the min output). So the set P_t of wires holding variables after layer t is the same for all variable values, |P_t| = h. Give each variable-holding position a *track* in {1..h}: a variable/constant comparator moves the track with the variable; a variable/variable comparator on wires p (min), q (max) leaves the tracks in place and acts as a generalized comparator from track(p) to track(q). Comparators in one layer use disjoint wires, hence disjoint tracks.
N sorts these inputs, so at the end the -infinity constants are lowest, the +infinity highest, and the variables appear sorted on the wires of P_d in wire order. Number the tracks by that order. The variable/variable comparators of layers 3..d then form a generalized network on h tracks of depth <= d-2 that sorts all inputs. By 1.4 there is a standard h-sorter of depth <= d-2. So D(h) <= D(n) - 2, and D(ceil(n/2)) <= D(h) by 1.5. QED

Remarks.
- The step "delete the constant wires" is not valid without the track/untangling argument: variables change wires when they meet constants. Two user-supplied write-ups of this lemma (a PDF and a README) were reviewed; the PDF skipped exactly this step, and its corollary had a misplaced parenthesis (correct: D(n) >= D(2) + 2(ceil(log2 n) - 1) = 2 ceil(log2 n) - 1).
- **Corollary (PROVED given LIT values D(13..16) = 9, D(17) = 10):** D(n) >= 11 for n = 25..32, >= 12 for n = 33..48, >= 13 for n = 49..64. Dobbelaere's table lists 10 for n = 18..32 (LIT). For n = 17..24 the lemma gives nothing new.
- EXACT slack s(n) = D(n) - D(ceil(n/2)) - 2: 0 at n = 3,4,5,6,9,10; 1 at n = 7,8,11..17.
- Novelty: not established. No source was found stating the inequality; a folklore (2 - o(1)) log2 n bound is cited in the literature (ECCC 2023/153, arXiv 2208.08394), so it may be known. Knuth 5.3.4 and Parberry were not read.

### 2.2 t-layer fixing theorem (PROVED)

A *valid t-fixing* of a network is an assignment of constants -infinity/+infinity to n-h input wires such that no two variables are compared in layers 1..t. **If a depth-d sorter has a valid t-fixing with h variables then D(h) <= d - t.** Proof: identical to 2.1 with "layers 1, 2" replaced by "layers 1..t". QED
Write maxV_t (or P(t)) for the largest h. Necessary condition C_t for a depth-d sorter: P(t) <= M(d-t). For (n,d) = (32,11): P(t) <= 16, 12, 10, 8, 6, 4, 4, 2 for t = 2..9.

Further facts:
- (AGENT, T1/T2) Max valid 2-fixing = n - nu(F u L) where nu is the matching number; for F perfect this is n/2 for every L, with 2^c maximum fixings (c = number of cycles of F u L).
- (AGENT, T1) beta_t(n) = min over t-layer prefixes of maxV_t satisfies ceil(n/2^ceil(t/2)) <= beta_t <= n/M(t), with equality to n/M(t) for t = 1,2,3,4,6. So no universal t-layer lemma with t <= 6 beats rate 2 log2 n; t >= 7 open.
- **Profile monotonicity (PROVED, "THM A"):** P(t+1) <= P(t) and P(t+1) >= ceil(P(t)/2). Proof: (<=) a valid (t+1)-fixing is a valid t-fixing. (>=) Replacing one variable by a constant changes no other token's trajectory, so take a valid t-fixing with position set W after layer t, |W| = h; layer t+1 has at most floor(h/2) comparators inside W; replace one end of each by a constant. QED
- **Hitting criterion (PROVED, "THM B"):** P(t+1) >= k iff some valid t-fixing with exactly k variables has a position set after layer t containing no comparator of layer t+1. Proof: (=>) reduce to exactly k by the replacement argument; (<=) clear. QED

### 2.3 Subcube rule (PROVED; agent A1's "SUBCUBE")

Let R_k be the set of 0-1 vectors reachable after k layers of a depth-d sorter. A *subcube* of dimension h is a set of vectors with n-h coordinates fixed and h free. **R_k contains no subcube of dimension > M(d-k).**
Proof. Let the cube have free wires W. The remaining d-k layers sort every vector of the cube. A comparator between a free wire and a fixed 0 or 1 routes the free value independently of its value (0 takes the min output, 1 the max). Track the h free values as in 2.1: the free/free comparators form a generalized network on h tracks of depth <= d-k; the final positions of the tracks are a fixed set of wires, and since the whole output is sorted the track values are sorted in wire order. So it sorts all 2^h 0-1 inputs, hence all inputs, and untangles to a standard h-sorter of depth <= d-k. So h <= M(d-k). QED
It implies the fixing rule and is strictly stronger on some small prefixes (AGENT).

### 2.4 Existential hitting rule (PROVED; "Lemma H", rule H-R1)

**If R_k contains a cube with free set W, |W| = h, then layer k+1 must contain at least h - M(d-k-1) comparators with both ends in W.**
Proof. Let e be the number of comparators of layer k+1 inside W. For each, fix its min-wire variable to 0. The sub-cube of dimension h-e is mapped by layer k+1 to a cube of dimension h-e: inside comparators now pair a 0 with a free variable, and comparators with one free end and one constant end only move the free variable. So R_(k+1) contains a cube of dimension h-e, and 2.3 gives h - e <= M(d-k-1). QED
Use: an exhaustive search over edge sets decides whether *any* next layer satisfies all cube constraints, killing a prefix for all possible next layers at once.

**Unsound variant (RETRACTED).** The two-layer inequality c_(k+1)(U) + c_(k+2)(U) >= |U| - M(d-k-2), counting comparators of both layers inside the original support U, is false: after layer k+1 the free set is no longer inside U. It is violated by the true layers of real depth-9 16-sorters (EXACT). No sound lookahead that kills a layer-4 prefix without choosing layer 5 is known.

### 2.5 Residual recursion and equivalences (P2)

- **Residual recursion (PROVED by 2.2):** for a depth-d sorter on n = 2h wires with perfect first layer and any maximum valid 2-fixing V, the untangled restriction Res(V) is an h-sorter of depth <= d-2; the first j layers of Res(V) are the untangled restriction of layers 3..2+j. Every fixing-size condition on Res(V) is implied by the n-level fixing filter; the only new information is exact membership of residual prefixes in the set of extendable prefixes (needs SAT data).
- **Equivalence of 2-layer prefixes (PROVED):** a prefix (layer 1, layer 2) extends to a depth-d sorter iff the prefix obtained by relabeling wires, by reversing any layer-2 comparator, or by reflection does. Proof: relabeling is trivial for generalized networks plus 1.4; reversing a layer-2 comparator (a,b) is the untangling move (swap labels a,b in all later layers and in the output order; other layer-2 comparators are disjoint from a,b); reflection is 0-1 duality. QED
- **Monotonicity in layer 1 (PROVED):** if (R1, R2) extends to a depth-d sorter then so does (R1 + c, R2) for any comparator c on two wires idle in R1. Proof: precede the sorter by c; its image is a subset of all inputs, and the depth is unchanged because the wires were idle. QED Layer 2 is not monotone (AGENT).
- **Green blocks (PROVED by direct trace for the 4-cycle; EXACT beyond):** block on wires 0..3 with layer 1 (0,1),(2,3) and layer 2 (0,2),(1,3). The two maximum fixings V = {0,3} and V = {1,2} both give the type pattern (-inf, V, V, +inf) after layer 2: for V = {0,3}, wire 1 = +inf and wire 2 = -inf, and layer 2 moves -inf to wire 0 and +inf to wire 3; for V = {1,2} layer 2 does nothing. So the residual networks coincide. Consequence (EXACT at n = 32): for Green layers 1-2 (8 blocks) all 256 maximum fixings give the same residual: layers 3.. restricted to the 16 wires w mod 4 in {1,2}. Non-alternating cycle types give two different patterns per cycle (EXACT enumeration to length 8). Conjecture (open): in tight cases only alternating cycle structures extend; matches the exact n = 10 data (only 5 of 152 second-layer orbits extend, all with min-min/max-max 4-cycle blocks).

### 2.6 n = 32, depth 11: state of the question

No depth-11 network found, none ruled out. D(32) >= 11 (2.1), best upper bound 14.
- (EXACT, two agents agree) The 4-layer Green hypercube prefix has maxV_4 = 12 > 10, so **any 32-sorter starting with those four layers has depth >= 12**. Bitonic prefix passes t = 3..8, fails t = 9.
- (EXACT) Hypercube layers 1-3: R_3 is a product of four 8-wire blocks (20^4 vectors), symmetry group of order 31,104; about 4.5% of the 31!! perfect layers 4 pass the hitting test (about 8.6e15, >= 2.8e11 orbits). Exhaustive enumeration is infeasible.
- (EXACT per prefix) Of 365 sampled 5-layer prefixes (hypercube layers 1-3, uniform admissible layers 4, 5), 364 have no admissible layer 6 (each an exhaustive proof for that prefix); one survivor (sample 79) unresolved after about 90,000 completions. For prefix cand4_32 plus 21 tested layers 5: no layer 6. An independent verifier re-derived the lemma, the subcube theorem, Lemma H and one headline instance with its own code.
- (SIM, calibration) Random prefix descent also stalls around layers 5-6 at depths where sorters exist (n = 12, 14, 16), so "dies at layer 5-6" is **not** evidence that depth 11 is impossible.
- (EXACT) Fixing profiles P(1..d) of optimal sorters: n = 8: 4 4 2 2 2 1; n = 10: 5 5 3 3 2 2 1; n = 12: 6 6 4 4 3 2 2 1; n = 16: 8 8 6 6 4 4 2 2 1 (tight against M(d-t) for every t >= 4).
- (AGENT, n <= 12) Pair-weight obstruction: depth D(n)-1 cannot sort the two central weight classes; explains 126 of 147 non-extendable 2-layer classes at n = 10.
- Not proved: D(2n) >= D(n) + 3 (would give D(32) >= 12).
- **RETRACTED:** "the multi-level conditions prove D(12) >= 8" (DFS bug). Correct: n = 8, d = 5 dies exactly at t = 5; n = 10, d = 6 dies at t = 2; n = 12, d = 7 not established.
- Searchers (annealing, home-made CDCL/CEGAR) do not get near depth 11-13 at n = 32 (SIM).

### 2.7 n = 32, depth 13 (in progress; notes E6, E7)

Best known: 14 at n = 32, 13 for n <= 28 (Wang, arXiv 2511.04107, LIT).
- Sound necessary conditions at (32,13) (cube thresholds 16, 12, 10, 8, 6, 4, 4, 2, 2 for k = 4..12; cone rule; last layers) all have slack on sensible prefixes: no obstruction visible.
- (EXACT) Profile of Wang's 28-wire network: tight on the cube rule at k = 9..12 and on the cone rule at k = 10..12; the last four layers are a forced halving cascade.
- (PROVED, short) A depth-13 network cannot contain two sorted halves at layer 8 or 9: merging two sorted 16-lists needs 5 layers since a wire then has 17 possible ranks > 2^4.
- SAT encoding (reflection-symmetric free layers, last layer adjacent only, penultimate span <= 3) validated on Wang's network. Results so far (solver answers pasted by the user, UNSAT not proof-certified): 12 specific 32-wire prefixes with layers 7-8 chosen by greedy profile scores are UNSAT for symmetric completions. On 28 wires every greedily chosen layer 7 that beats Wang's on those scores is also a dead end, so these UNSATs say nothing about depth 13 in general. Four 7-free-layer instances and a third batch had no reported result at the time of writing.
- (SIM) Reflection symmetry can exclude solutions for a fixed prefix labelling.

### 2.8 Last layers

- **Last-layer comparators are adjacent (LIT: Codish, Cruz-Filipe, Schneider-Kamp; EXACT here for n = 4, 5).** In a sorting network, every non-redundant comparator of the last layer is (i, i+1).
  **FLAWED proof in note P2:** it exchanges two input values j and k and claims the network "routes values obliviously"; that holds only for adjacent values that are never compared directly, which the proof does not establish. Use the literature proof. The n = 4, 5 check (all reachable 0-1 sets under comparator sequences, no set that a single non-adjacent comparator completes to sorted) is in this session.
- **Consequence (PROVED given the above):** after layer d-1 each weight class has at most 2 reachable vectors: the sorted one, and the sorted one with the boundary pair swapped. Proof: the pre-last vector y differs from the sorted s (with a zeros) exactly on swapped pairs (m, m+1) with y_m = 1, y_(m+1) = 0, s_m = 0, s_(m+1) = 1, which forces m = a-1. QED Since last-layer comparators are disjoint, two consecutive weights never both have 2 vectors, so |R_(d-1)| <= (n+1) + ceil((n-1)/2) (49 at n = 32).
- Counting rules are vacuous before the last 2-3 layers (EXACT numbers in note P2/P).

---

## 3. Asymptotic lower bounds

Record: (3.27 - o(1)) log2 n (Kahale, Leighton, Ma, Plaxton, Suel, Szemeredi, STOC 1995; LIT). No later improvement found. Yao 1980: 2.41 log2 n (LIT). A 4 log2 n bound was attempted and **not obtained**.

### 3.1 Minterm potential (PROVED here; replaces L1's weight recursion)

For a wire at a given time let m = the least size of an input set S such that the wire holds 0 whenever all inputs in S are 0 (0-1 view).
(a) The wire can hold a value < m: put the values 0..m-1 on S; thresholding at m gives zeros exactly on S.
(b) At a comparator with inputs m_a <= m_b: the min output has m <= m_a, the max output has m <= m_a + m_b <= 2 m_b.
(c) **Potential inequality.** For alpha > 0 let Phi_alpha(t) = sum over wires of m^(-alpha). Then Phi_alpha(t) >= n G^t with G = (1 + 2^(-alpha))/2.
Proof of (c). Phi(0) = n. At a comparator, new contribution >= m_a^(-alpha) + 2^(-alpha) m_b^(-alpha) >= G (m_a^(-alpha) + m_b^(-alpha)), because the difference is ((1 - 2^(-alpha))/2)(m_a^(-alpha) - m_b^(-alpha)) >= 0. Idle wires keep their term. QED

### 3.2 The weight recursion of note L1 is false (PROVED by counterexample)

L1 claimed: with N_k(t) = number of wires with m <= 2^k after t layers, N_k(t+1) >= (N_k(t) + N_(k-1)(t))/2, hence N_k(t) >= n P(Bin(t,1/2) <= k). The justification ("a wire leaves the class only as the max output of a pair (<= k, = k)") only gives N_k(t+1) >= N_(k-1)(t): a weight-k wire paired with a lighter wire leaves, and nothing forces half of them to stay.
Counterexample: 4 wires, layer 1 (0,1),(2,3), layer 2 (0,3),(1,2). After layer 2, wire 3 holds max(min(x0,x1), max(x2,x3)), whose least zero-forcing set has 3 elements, and it cannot hold a value < 2 (it would need max(x2,x3) <= 1 and min(x0,x1) <= 1 with one of them equal to 1, impossible with distinct values); same for wire 2. So only n/2 wires have m <= 2, against the claimed 3n/4.
Consequences: L1's "reconstruction" of 3.27 and its formula 1 + A H(1/A) are unproved. The numbers it computed (3.2706 = 1/(1 - log2 phi), and the "finishing rate" targets below) reproduce the published constants, so the published proof presumably uses a correct binomial-type statement under a different definition; that paper's depth section must be read directly.

### 3.3 What 3.1 does give (PROVED, using one LIT fact)

LIT fact (Knuth 5.3.4 ex. 25): the set of values a wire can hold is an interval.
**Counting step.** s layers before the end, for every i, at most 2^i + 2^s wires have m <= 2^i. Proof: such a wire can hold a value < 2^i (3.1a), reaches at most 2^s outputs (1.6), and holds an interval of values, so all its values are < 2^i + 2^s; on one permutation input these wires hold distinct values. QED
Hence at time tau = T - s (T = depth): Phi_alpha(tau) <= 2^s + C_alpha n^(1-alpha) for 0 < alpha < 1, and <= 2^s + O(log n) for alpha = 1 (order the wires by m; the j-th wire beyond the first 2^s has m > j/2).
- **Yao's bound.** s = 0, alpha = 1: n (3/4)^T <= 1 + O(log n), so T >= log_(4/3)(n / O(log n)) = (2.409 - o(1)) L.
- **3 log2 n.** Let g(alpha) = log2(1/G) = 1 - log2(1 + 2^(-alpha)); g(alpha) ~ alpha/2 as alpha -> 0. If tau g(alpha) < alpha L - c then n G^tau > 2 C_alpha n^(1-alpha), so 2^s >= n G^tau / 2, i.e. s >= L - tau g(alpha) - 1. Take tau = (2 - delta) L (allowed for small alpha, since alpha/g(alpha) -> 2): T = tau + s >= (2 - delta) L (1 - g(alpha)) + L - 1. Letting alpha, delta -> 0: **T >= (3 - o(1)) L.** (If T < tau, apply the s = 0 case to get T >= (2 - o(1)) L and repeat with tau = T; the conclusion is the same.)
- With this potential alone the optimum over tau is 3 (at tau = 2L), not 3.27.

### 3.4 What 4 log2 n would need (heuristic, from L1; numbers rest on the unproved binomial form)

If the second half of the argument could be charged at c' levels per bit instead of 1, the optimisation would give 3.27 (c' = 1), 3.67 (1.44), 4.00 (1.79), 4.20 (2). A finishing lemma at rate 1.79 is false unconditionally (before Batcher's last merge every wire straddles the median and one merge finishes), so it would need a richness condition on what a cheap first half leaves behind. Other routes considered and why they stall: universal fixing recursion needs t >= about 30 layers of exact data; counting gives 2L; formula-depth bounds stop near 2L.

---

## 4. Constructions for fixed n

### 4.1 Base sorter (EXACT on 2^16 inputs)

Depth-9 16-sorter with first layer (0,1),(2,3),..,(14,15), 61 comparators:
```
L1 (0,1)(2,3)(4,5)(6,7)(8,9)(10,11)(12,13)(14,15)
L2 (0,2)(1,3)(4,6)(5,7)(8,10)(9,11)(12,14)(13,15)
L3 (0,4)(1,5)(2,6)(3,7)(8,12)(9,13)(10,14)(11,15)
L4 (0,8)(1,9)(2,10)(3,11)(4,12)(5,13)(6,14)(7,15)
L5 (1,2)(3,12)(4,8)(5,10)(6,9)(7,11)(13,14)
L6 (1,4)(2,8)(3,10)(5,9)(6,12)(7,13)(11,14)
L7 (2,4)(3,8)(5,6)(7,9)(10,12)(11,13)
L8 (3,5)(6,8)(7,10)(9,12)
L9 (3,4)(5,6)(7,8)(9,10)(11,12)
```

### 4.2 Mergers

M(k,m) = minimum depth of a network merging k sorted lists of length m.
- **Base (PROVED).** If a depth-d sorter on 2k wires has first layer (0,1),(2,3),.., then its layers 2..d merge k sorted pairs: M(k,2) <= d-1. Proof: layer 1 fixes every input consisting of sorted pairs, so the rest sorts them. QED Conversely a pair layer followed by any merger of k sorted pairs is a 2k-sorter, so M(k,2) >= D(2k) - 1. With 4.1: M(8,2) = 8 (using D(16) = 9, LIT).
- **k-way odd-even step (PROVED; re-derived twice): M(k,2m) <= M(k,m) + ceil(log2 k).**
  Construction: merge the even-indexed elements of all lists (k lists of length m) and, in parallel, the odd-indexed elements. Interleave the results as e_0, o_0, e_1, o_1, ... Then apply layers {(2i+1, 2i+2s) : i} for s = 2^(t-1), ..., 2, 1 where 2^t >= k.
  Proof (0-1 principle). List i has z_i zeros; its even-indexed part has ceil(z_i/2) zeros and its odd-indexed part floor(z_i/2). So the sorted even sequence has Ze zeros, the odd one Zo zeros, with d := Ze - Zo = number of lists with z_i odd, 0 <= d <= k. The interleaved sequence is 0^(2b) (01)^d 1^* with b = Zo.
  Claim: if d <= 2s, the layer with parameter s produces 0^(2b') (01)^(d') 1^* with d' <= s. Use offsets from position 2b: zeros at even offsets 0, 2, .., 2d-2, ones at odd offsets 1, 3, .., 2d-1, all ones beyond. The comparator from odd offset 2j+1 to even offset 2j+2s swaps iff it sees (1,0), i.e. iff 0 <= j and j + s < d. If d <= s nothing swaps and d' = d <= s. If d > s the swaps j = 0..d-s-1 put zeros on odd offsets 1..2(d-s)-1 and ones on even offsets 2s..2d-2. Since d <= 2s, offsets 0..2(d-s)-1 are now all zero, offsets 2(d-s)..2s-1 are still (01) pairs, 2s - d of them, and everything from offset 2s on is one. So d' = 2s - d < s. Comparators that start before offset 0 see a 0 on their min side and do nothing.
  Initially d <= k <= 2 * 2^(t-1). After the layer s the invariant d <= s = 2(s/2) holds for the next layer. After s = 1, d <= 1, and 0^(2b) (01)^1 1^* is sorted. Each layer is a matching (each odd position is a min-end once, each even position a max-end once). QED
  Hence M(8,m) = 3 log2 m + 5 and M(16,m) = 4 log2 m + 9 as upper bounds for m a power of 2.
- (AGENT, home-made CDCL, UNSAT not proof-logged) Exact values M(3,2..5) = 4,5,6,6; M(4,2) = 5; M(4,3) = 6; M(5,2) = 6; M(6,2) = 7. Upper bounds M(4,4) <= 7, M(8,8) <= 14, M(16,2) <= 13. The cleanup after two merged sub-lists cannot be shorter than ceil(log2 k) for k = 3,4,8,16, so any gain must interleave the phases.
- (AGENT) Lower bounds are only cone-type: about log2(km). Every known merger costs about log k * log m.

### 4.3 Sorters beyond 64 wires

| n | Batcher | here | size | how | status |
|---|---|---|---|---|---|
| 128 | 28 | **26** | 1439 | 8 blocks of 16 (depth 9) + M(8,16) = 17 | EXACT (two independent ways, below) |
| 256 | 36 | 34 | 3775 | 16 blocks of 16 + M(16,16) = 25 | AGENT; follows from Lee-Batcher's formula |
| 512 | 45 | 43 | 9599 | 8 blocks of 64 (depth 20) + M(8,64) = 23 | AGENT + 4.2; follows from Lee-Batcher's formula |
| 1024 | 55 | **52** | 23679 | 8 blocks of 128 (depth 26) + M(8,128) = 26 | EXACT (compositional certificate, below) |

**Certification of 128 and 1024 (EXACT; this session).** The networks were rebuilt from 4.1 and 4.2 (appendix A; sizes equal those recorded for the earlier files, which were not available for a direct comparison). A separate checker (appendix B) reads only the flat layer list and:
1. finds the blocks as connected components of the first layers and checks every 16-wire block on all 2^16 inputs;
2. for every merger, requires the layers before its last three to split into exactly two components holding the even- and odd-indexed wires of each list, recurses on both, checks base mergers (8 sorted pairs, 8 layers) on all 3^8 inputs, and checks the last three layers on every pair of zero counts (Ze, Zo) with 0 <= Ze - Zo <= 8;
3. requires every comparator to be accounted for and none to cross a group boundary.
**Soundness (PROVED).** By induction each sub-merger sorts all sorted-list 0-1 inputs: the two halves do by induction, their outputs are sorted on their own wires with Ze - Zo equal to the number of odd lists, which lies in [0,8], and step 2 checked exactly those inputs for the last three layers. Blocks sort by step 1. The 0-1 principle finishes. Only the trivial counting fact is used, not the general theorem.
Result: n = 1024: 64 block sorters, 128 base mergers, 119 cleanup steps, 23679 of 23679 comparators: certified. n = 128: certified. Six negative controls (one comparator dropped in layers 6, 31, 41, 46, 52, 52) rejected.
Cross-checks: the 128-wire merger on all 17^8 = 6,975,757,441 sorted-block inputs in separate C code that assumes no structure: 0 failures (209,160 failures with one comparator dropped). Full 1024 network on 49,152 arbitrary and near-sorted 0-1 inputs: 0 unsorted.

**Prior art (LIT, abstracts only).** The k-way step is Lee and Batcher's multiway merge (1994/95): k lists of length n in T(k) + ceil(log_m n) ceil(log2 k) ceil(log2 m) steps. With m = 2 that formula gives 27 at n = 128 and 53 at n = 1024 (my arithmetic). The one layer saved comes from starting at sorted pairs with M(8,2) = 8 instead of T(8) + 3 = 9. No source was found stating 26 at 128 or 52 at 1024, and no table of depths beyond 64 inputs (Dobbelaere's list stops at 64). Absence of a hit, not proof of novelty.

### 4.4 n <= 64 (note E1)

Merge-based search with exact per-node certification matched the literature depths for n = 18..36 and 45..64 and was one layer worse for n = 37..44 (17 and 18 against 16 and 17). No improvement for any n >= 18. Networks for n <= 35 were also verified by full exhaustive check. A merge of a + b = n needs at least ceil(log2 n) layers after its inputs finish, so the literature's depth 16 at n = 37..40 is not "sorters then merge". (EXACT) BFS reproduces optimal depths for n = 2..7.

### 4.5 AKS-style bag-tree network on 16 wires (EXACT)

A small instance of the AKS scheme (tree of bags, D = 6 circulant halvers with offsets 0,1,2,4,3,5, fringes (0,2,1,0) per level returning to the parent, 5 correcting stages then 3 descent stages): depth 17, size 106 after untangling and pruning, verified on all 2^16 inputs. Only the first halver is genuinely approximate at this size. Full layer listing in project note `AKS16_expander_bag_tree_network.md`. For comparison: exact-halver recursion depth 15, optimal 9.

---

## 5. Structure every O(log n) network must have

### 5.1 Span-schedule theorem (PROVED; note G4, re-derived in audit)

Let s_t be the largest b - a over comparators (a,b) of layer t of a standard sorting network of depth D. **For every tau >= 0: sum over t > tau of s_t >= n - 2^tau.**
Proof. Take S = S(0,tau) from 1.7, |S| = c <= 2^tau, and the input with ones exactly on S. After tau layers wire 0 holds a one. In each later layer the leftmost one stays or moves to its partner, so its position grows by at most s_t. The sorted output has its leftmost one at n - c >= n - 2^tau. QED
Meaning: after the first log2 n - 1 layers the remaining layers still need total span n/2. Long comparators must stay active to the end. AKS's return to the root is necessary; merge sort satisfies it through its last merge.

### 5.2 Span budget (PROVED; P5 3c)

Every sorting network has total comparator span >= n^2/4 (n even), so a depth-T network has mean span >= n/(2T).
Proof. For a permutation state sigma let A = sum_i |sigma(i) - i|. A swap on wires a < b changes |sigma_a - a| + |sigma_b - b| into |sigma_b - a| + |sigma_a - b|, a change of at most 2(b - a) by the triangle inequality. The reversal has A = n^2/2 and each comparator swaps at most once on that input. QED

### 5.3 Descent identity and a barrier for displacement potentials (PROVED; P5)

G(sigma) = (1/2) sum_i (sigma(i) - i)^2.
- **Identity:** a swapping comparator on a < b (sigma_a > sigma_b) lowers G by exactly (b - a)(sigma_a - sigma_b). Proof: (sigma_a - a)^2 + (sigma_b - b)^2 - (sigma_b - a)^2 - (sigma_a - b)^2 = 2(b - a)(sigma_a - sigma_b). QED
- **Barrier:** if one round of depth D satisfies G(after) <= rho G(before) for all states with rho < 1, then 2^D >= log_kappa(n/2), kappa = (1 + sqrt rho)/(1 - sqrt rho). So D >= log2 log2 n - O(1).
  Proof. State: items i and j = i + d exchanged, all else home; G = d^2. Item j starts on wire i and can end the round only on one of at most 2^D wires C(i). G(after) <= rho d^2 forces it within sqrt(rho) d of j, so some c in C(i) has d in [(c-i)/(1 + sqrt rho), (c-i)/(1 - sqrt rho)]. Each cone element serves a band of distances of ratio kappa; all d in 1..n/2 need log_kappa(n/2) bands. QED
  Consequence: a potential depending only on displacements cannot contract under constant-depth rounds. It needs a second term saying whether an item sits on a wire serving its scale; that term is AKS's tree level and strangeness. The tree can be made implicit, not removed.

### 5.4 Deficit matrix (PROVED statements; P6, checked numerically on 300 permutations)

M(r,c) = #{i < c : sigma(i) < r}, Delta(r,c) = min(r,c) - M(r,c).
1. Delta >= 0, and Delta = 0 iff sorted.
2. A swapping comparator on a < b lowers Delta by exactly 1 on the rectangle (sigma_b, sigma_a] x (a, b] and changes nothing else (only the count of items of rank < r left of c changes, and only for those r, c). So every entry is nonincreasing under every standard comparator.
3. Sum of all entries = G. The diagonal Delta(c,c) is the number of items that must cross cut c.
4. An eps-halver says Delta(k, n/2) <= eps k for k <= n/2.

### 5.5 Reduction to square merging (PROVED, folklore-level)

Let Msq(n) = depth to merge sqrt(n) sorted lists of length sqrt(n). Then T(n) <= T(sqrt n) + Msq(n), so Msq(n) <= c log2 n implies T(n) <= 2c log2 n; conversely Msq <= T. The standard recursion behind every merge-based sorter (Knuth 5.3.4), with multiway merging studied by Leighton (columnsort) and Lee-Batcher; not claimed new. Concrete targets: M(8,8) <= 13 (now 14), M(16,16) <= 24 (now 25), M(32,32) <= 37 (now 39).

### 5.6 Correcting errors (AGENT, note Round 4 / G5)

- After depth D some input has displacement >= ceil(n/2^D) - 1 (cone).
- An almost-sorter of depth a log n with displacement n^(1-delta) yields a sorter of depth ((a + 1 - delta)/delta) log n.
- Correcting one stray at an unknown place costs about 1.3 to 1.44 log2 n: lower bounds 3,4,5,7,8,9,11,12,13 for n = 4..1024 and a "Fibonacci insertion" network of depth 6,8,10,11,13,14,16,17 for n = 8..1024. Consistent with Stachowiak's 1.44 log2 N (LIT).

---

## 6. Halvers

A halver on n = 2H wires: for 0-1 inputs with k <= H ones, misplaced = ones left in the lower half (symmetric for zeros). eps = max over k of (max misplaced)/k. *Between-halves* halver: D layers, each a perfect matching between the lower half A and the upper half B, min to A.

**6.1 Stuck lemma (PROVED; "F4"/"L2").** After D between-halves layers, let S = set of A-wires holding a one. Then every wire of S and of N(S) (all partners of S over the D layers) holds a one, so |S| + |N(S)| <= r, the number of ones in the window.
Proof. An A-wire receives the min: once 0 it stays 0. A B-wire receives the max: once 1 it stays 1. A wire of S was 1 throughout, so each partner was 1 after their comparison and stays 1. QED

**6.2 Forced stuck sets (PROVED; "L3").** For any wiring and any S in A, the input with ones exactly on S and N(S) is unchanged by the halver. Proof: every comparator touching S has ones on both ends; comparators touching only N(S) have a one on the max side. QED

**6.3 eps >= 1/(D+1) for between-halves halvers (PROVED).** Take one A-wire and its at most D partners: D + 1 ones, one misplaced. QED (EXACT data: holds in every run; reached only when D is close to H.)

**6.4 eps >= 2^(-D) for any D-layer halver, any wiring (PROVED).** For a lower-half output wire v take the forcing set S(v,D) of 1.7 (location not needed), k = |S| <= 2^D. The input with ones exactly on S has k ones and a one on v, so eps >= 1/k >= 2^(-D) (if k <= H; otherwise D >= log2 H already). In particular an exact halver needs depth >= log2 n. QED
**Perfect halver depth >= log2 n (PROVED, direct).** An upper-half output u depends on a cone C of at most 2^D inputs. If |C| <= n/2, set C to 0 and put n/2 ones elsewhere: u equals its value on the all-zero input, 0, but must be 1. So 2^D > n/2. QED
**A sorter on n wires gives a perfect halver on 2n (PROVED, Batcher).** Sort both halves, then compare a_i with b_(n+1-i): the bitonic half-cleaner. 0-1 check: with s zeros in A and t in B, position i gets (0,0) iff n+1-t <= i <= s; the min side receives a zero whenever either input is zero, so it receives min(n, s+t) zeros. QED

**6.5 Exactness for few strays (PROVED + EXACT).** If the D partners of every A-wire are distinct, the halver is exact for every input with at most D ones. Proof: a nonempty stuck set S has |N(S)| >= D, so |S| + |N(S)| >= D + 1 > k. QED (EXACT at n = 16..32 for shift, offset-set, stride, cube wirings: first bad k = D + 1. Random matchings repeat partners and lose it.)

**6.6 Exact between-halves windows cost linear depth (PROVED).** A between-halves network on w + w wires that is an exact halver needs D >= w. Proof: with one one at A-wire i and one zero at B-wire j (all other A zero, all other B one), those two must be compared directly; a layer gives each A-wire one partner; all w^2 pairs are needed. QED (EXACT: w = 2..9, only the complete wiring works.)

**6.7 The leak is a floor, not a contraction (EXACT, n = 16..32).** Worst leftover as a function of strays going in is min(a, g(k)) with g growing in k; at dense k every stray stays stuck; ratio after/before = 1.0 in every table. For consecutive shifts the worst leftover is floor((k-D+1)/2). No static localization: for every k > D the set of wires that can hold a misplaced value is all of them, even for near-sorted inputs.

**6.8 Wiring data (EXACT, n = 20).** Best circulant offset sets beat consecutive shifts and random matchings at equal depth (D = 5: .222 vs .300 vs .327; D = 7: .125 = 1/(D+1)). Best sets look like D-1 consecutive offsets plus one far offset. Small-n values overestimate asymptotic eps and should not be extrapolated. One within-half design tried: worse. Two-block (shift then stride): worse.

**6.9 Barriers on halver-based proofs (AGENT, note Round 3).** Any proof contracting stranger mass by c*eps per halver round costs depth >= 3.0 log2 n at c = 2 with ideal eps and >= 12.4 log2 n with certified random halvers. Aligned-only window networks cannot sort when s(j(j+1)/2 + 1) < log2 n ("cut lemma"). Proofs not available.

**6.10 Expansion gives contraction away from the threshold (PROVED; "L4").** If |N(S)| >= gamma |S| for all S in A with |S| <= alpha H, then every input with r <= (1 + gamma) alpha H ones in the window leaves at most r/(1 + gamma) ones in A. Proof: if the stuck set S had more than alpha H elements take S' in S of size ceil(alpha H); S and N(S') are all ones, so |S| + gamma alpha H <= r, contradiction; otherwise 6.1 gives (1 + gamma)|S| <= r. QED Here r counts all ones in the window, so this is proportional only where all ones are strays.

---

## 7. The sliding-window descent: refuted

Design (notes D5, Round 3, G4): n = 2^k; level l has bags of m = n/2^l wires; a round at bag size m applies, for i = j..0, aligned then half-shifted windows of 2^i bags, each with d between-halves matching layers; depth per round 2d(j+1).

**7.1 Fixed (d, j) fails for every wiring (PROVED).**
- Lemma ("L5"): if comparators of a group are confined to disjoint windows of width w, the leftmost one moves by less than w. Proof: if the leftmost one is in a window, the ones of that window stay in it. QED
- **Corollary S1.** With E extra rounds at m = 2, if n > 2^(2d(j+1)(j+4)+1) + 2^(j+4) E then some 0-1 input is not sorted. Proof: let tau <= 2d(j+1)(j+4) be the number of layers in levels 0..j+3 and take x = S(0,tau) from 1.7. Each later level with bag size m has groups of total width < 2^(j+2) m; later bag sizes sum to < n/2^(j+3); extra rounds add 2E. So the leftmost one ends left of n/2 + 2^(j+3) E, but sortedness needs it at n - 2^tau or beyond. QED
- Corollary S2: j >= sqrt((log2 n - 2)/(2d)) - 4, so depth is at least about sqrt(2d) log2^1.5 n.
- **THM S' (closure fails for large bags).** For bag size m >= 2^tau/nu the class K_m(nu,R) (at most nu m strays per side, none more than R bags from the threshold) contains an input no continuation sorts. Proof: u = first wire of a bag, p0 = u + 2m, S = S(u,tau), x = ones on S and on [p0, n). Its strays lie in S, so x is in the class; wire u holds a one for tau layers and afterwards the leftmost one advances by less than m, but the threshold is at least m away. QED

**7.2 Concrete failures (SIM, each verified by running the network).** The min-support adversary (1.7 with the smaller-set rule, then 1.8) finds unsorted inputs for random wirings at (d,j) = (1,2) from n = 256-512, (1,3) and (2,2) at 2048, (1,4) and (3,2) at 8192, (2,3) at 32768. Every surviving configuration is deeper than Batcher. **RETRACTED:** Round 3's "6 log2 n + 12 empirical" (weak adversary).

**7.3 Union bound over inputs cannot close one round (PROVED; "THM N").** Let h = m/2, nu < 1/2, a0 = floor(nu h) + 1, b = h - a0 - 1, and X = inputs that are 0 left of an interior bag T, 1 right of it, with a0 ones in T's left half A and b ones in its right half B. These have no strays, |X| = C(h,a0) C(h,b), and for fresh uniform matchings each fails (leaves more than nu h strays) with probability >= [C(b,a0)/C(h,a0)]^d.
Proof. T is unchanged until its own aligned scale-0 group (at coarser scales every T-wire's partner outside T is a one on the max side or a zero on the min side). If each of the d matchings maps the a0 one-wires of A into the b one-wires of B nothing moves (6.2) and a0 strays remain; the d events are independent. QED
By Stirling the sum of failure probabilities exceeds 1 whenever 2H(nu) > d beta(nu), beta(nu) = (1-2nu)ln(1-2nu) - 2(1-nu)ln(1-nu): all d <= 13 at nu = 1/4.
**Deterministic companion (PROVED, "THM B"):** any closed class has nu >= 1/(d+1) - 1/h at distance 1 (from 6.1/6.2 and |N(S)| <= d a0).

**7.4 Monotone domination does not compress (PROVED; "THM C").** Covering a class of stray placements (a = nu m strays in a zone of Rm wires) by dominating representatives needs at least (R/(nu + D + tau))^(nu m) of them. Proof by counting: a representative y with at most tau m ones left of cut p - Dm has at most a + (D + tau) m ones in the zone and dominates at most C(a + (D+tau)m, a) of the C(Rm, a) stray sets. QED
**False (counterexample):** "moving ones to the right makes an input easier". Comparator (0,2) on 3 wires: 100 -> 001 sorted, 010 stays 010.

**7.5 Constant-depth cleanup (PROVED; "F5").** If all strays lie in an interval of width <= B/2, B = 2^b, then sorting every aligned block of B wires and then merging the two halves of every half-shifted block sorts; depth b(b+3)/2 with Batcher. Proof: the dirty interval lies in an aligned block, or straddles one boundary kB, and then by 1.3 the disorder stays in [kB - B/2, kB + B/2), a shifted block with two sorted halves. QED

**7.6 Other facts from D5.** Under worst-case landing the cascade of window sizes absorbs strays at bag distance <= 2^j - 1 and the no-return distance is 2^(j+1) - 2 bags (EXACT residue check, j <= 6). A lazy but valid eps-halver leaves far strays in place, so no proof can use only the eps-halver property.

---

## 8. AKS, Paterson, Seiferas: simplification and constants

### 8.1 The scheme (LIT)

Binary tree of bags over the sorted order. Bag at depth d at stage t has capacity b = n nu^t A^d. Each stage every bag applies a separator, sends floor(lambda b) items from each end to its parent and the two halves of the rest to its children. Strangeness of an item = levels it must climb to reach a bag whose interval contains it. Seiferas's invariant (Algorithmica 2009; read in full): (1) alternate levels empty, (2) equal counts per level, (3) contents <= capacity, (4) at most lambda eps^(j-1) b items of strangeness >= j. Constraints: nu >= 4 lambda A + 5/(2A); nu >= 2 A eps + 1/A; and a third one (8.2). Sample: A = 10, lambda = eps = 1/100, nu = 0.65: about 6.95 log2 n stages.
"Nothing moves": a bag is a set of wire positions; moving to the parent means those wires join the parent's comparator group at the next stage.

### 8.2 A missing term in Seiferas's third constraint (PROVED by example; audited)

His bound on natives sent to the wrong child counts the excess of sibling-natives over half plus halving errors. It omits that a bag's own small strangers displace natives across the middle. Example with exact sorting: 100 items, 5 small strangers, 50 natives of the left half, 45 of the right: positions 0..4 hold strangers, so 5 left-natives land in the upper half although the excess is 0.
Corrected constraint: lambda nu >= 2 lambda eps A + lambda/A + eps/(2A) + 2 lambda eps A/(1 - (2 eps A)^2) + 2/(8A^3 - 2A).
His theorem and first sample point survive; his second sample point (A = 6.785, coefficient 238,198) and the optimum of the printed constraints do not. Paterson's corresponding inequality has the term (LIT).

### 8.3 Energy proof of Seiferas's network (statement AGENT-level: proof was in a 4-page PDF not available here)

Energy of a bag E(B) = sum over its items of mu^strangeness, lambda = 1/mu. Invariant: alternate levels empty, equal counts, and E(B) <= capacity. Claim: preserved for A >= 16, mu = A^2, eps <= A^(-4), nu >= 12/A; stages <= ((1 + log2 A)/log2(A/12)) log2 n; finish with 4-sorters.
Ledger per bag of capacity b: fringes from two children 6Ab/mu + 2; natives from the parent b/(2A); natives sent the wrong way mu (u + lack + aliens + eps b/(2A)); parent's strangers mu eps b/A; total/b <= 6A/mu + 7/(2A) + mu/(4A^3 - A) + (2A/mu)/(1 - (2A/mu)^2) + 3 mu eps/(2A) < 12/A.
E <= b gives at once: at most b items; at most b mu^(-j) items of strangeness >= j; strangers fit in one fringe. One constraint instead of three; constants worse (lambda = 1/256, eps = 1/65536 at A = 16). A re-derivation, not a new theorem. (SIM) item-level simulation n = 2^8..2^14: max E/capacity 0.36 with exact separators, at most 0.84 with every split erring maximally at eps = 0.02.

### 8.4 "Guessing bits" restatement (no new mathematics)

Each item has an address (a bit string, its current guess for the leading bits of its rank), weight mu^(error length). One stage, for the items sharing an address with budget B = n nu^t A^d and f = floor(B/mu): split the row at the middle, keep splitting the two end pieces in half until they have f items; the first and last f items lose their last bit; of the rest the lower half append 0, the upper half append 1. Dictionary: address = tree node, losing a bit = sent to parent, error length = strangeness, budget = capacity, cascade of splits = separator. The single primitive is the eps-split at a cut. One halver per stage instead of the cascade fails in simulation even with exact halvers (SIM, one design).

### 8.5 Retention lemma (PROVED; P8)

Rule: every bag cuts its contents into FL | CL | MID | CR | FR; fringes go to the parent, MID stays, CL and CR go to the children. lack(B) = |I_B| - (items held in B's subtree).
**Lemma.** Assume exact separators, all bags at one depth have the same size, every item is in a bag whose interval contains its rank, and MID >= lack(B) in every bag. Then the same holds after one stage.
Proof. Fringes and MID are harmless. Let h = |B| and l = number of B's items native to the left half I_L. The |I_B|/2 natives of I_L sit in the left child's subtree (which holds only such items, s of them), in B, or in ancestors (a_L of them): l = |I_B|/2 - s - a_L. Likewise r = |I_B|/2 - s - a_R, with l + r = h and a_L + a_R = lack(B). So l = h/2 + (a_R - a_L)/2 and |l - h/2| <= lack(B)/2. CL occupies positions [f, (h - MID)/2), below l because MID >= lack(B); same for CR. QED
Identity: sum over bags of lack(B) = sum over items of levels still to descend.
- (EXACT, per n) A deterministic integer schedule built on this (budgets beta_t(d), invariant X_j(B) <= delta^(j-1) beta_t(d)) satisfies its certificate inequalities for every L up to 128 at eps = 1/100 with T <= 3.4 L - 2 stages. Termination in O(log n) stages for all n is **not proved**; existence of the five-way separators is assumed.
- **RETRACTED:** P8's contraction rate 2 sqrt(eps(1-eps)); the proved homogeneous rate is eps + 2 sqrt(2 eps), below 1 only for eps < 0.1006.
- Relation to Seiferas: retention changes where the imbalance is paid (size of the retained band instead of the 1-stranger budget), not the counting. His proof is complete for all n; this one is not.

### 8.6 Why a capacity schedule is needed (PROVED identity + SIM; P6, P7)

Work per 0-1 threshold p; a bag is left, right or on the path of p.
- **Conservation (PROVED):** with S_L = ones in left bags, S_R = zeros in right bags, Z_path = zeros in path bags, Q = p - (holdings of left bags): Z_path - Q = S_L - S_R. Proof: zeros total p = (holdings of left bags - S_L) + Z_path + S_R. QED
- A path bag can legitimately hold more zeros than its split can route correctly; the surplus is bounded by half the mass held above it plus strays (P7 identity), and goes to the wrong child as real strays. **RETRACTED:** P6's statement that these new strays are an accounting artefact.
- (SIM, fluid single-threshold model, fixed greedy adversary) Schedule-free designs fail even with perfect separators. Paterson's schedule at Jerabek's parameters has peak stray load 13-17% of the fringe. Fastest workable schedules: 2-3.3 stages per level at eps = 0, 5-8 at eps = 0.05, essentially none at eps = 0.15; A >= 3 needed once eps > 0.

### 8.7 Invariant versus potential (argued, P5)

Normalised stranger counts obey x' <= M x for a nonnegative operator M. Paterson's invariant is a right sub-eigenvector (a weighted max norm contracts by nu); a sum potential is a left sub-eigenvector; by Perron-Frobenius the rates agree. For strangeness >= 2 alone the rate is 2 sqrt(2 eps); the slow number is the capacity drain nu. A potential rewrite can remove bookkeeping, not the constant.
**Accounting barrier (heuristic, P6):** a potential that only sees bag membership earns at most 1 - H(eps) bits per item per halver, and with eps >= 1/(D+1) at most about 0.14 bits per comparator, i.e. at least about 14 log2 n layers. Beating Batcher at n <= 1024 needs about 0.33.

### 8.8 Depth coefficients (c in depth <= c log2 n)

| source | c | status |
|---|---|---|
| Paterson | about 6100 (counts layers; reproduced 6026 from his formulas, conditional on one garbled condition) | LIT + AGENT |
| Chvatal | about 1830 (M-sorters; N >= 2^78) | LIT, abstract only |
| Seiferas, his sample | 514,246; "6.05" and "6.95" count stages, not layers | EXACT arithmetic from his formulas |
| Seiferas, corrected constraints, optimum | 281,084 | EXACT arithmetic |
| same architecture, better bookkeeping and partial-range halvers | about 6,300 (conditional 5,518) | AGENT, long unreviewed chain |
| retention schedule, computed budgets | about 31,000, per-n certificates | AGENT |
| block-sort separator (deal, sort blocks of M, lay out by rank) | about 1,000-1,300 | SIM estimate, no proof; probably Chvatal's mechanism |

The coefficient is dominated by the separator (rounds times halver depth). Multi-bit variants of the stage hurt (SIM). As real networks at n <= 1024 the scheme is 1.4 to 3.9 times deeper than Batcher (best found 14, 34, 59, 85, 116, 161, 215 for n = 16..1024; EXACT only for n <= 32).

---

## 9. Retractions and corrections in one place

1. Sliding-window "6 log2 n + 12 empirical": withdrawn (7.2).
2. "D(12) >= 8 by multi-level conditions": bug (2.6).
3. Two-layer lookahead inequality: unsound (2.4).
4. P8 contraction rate: should be eps + 2 sqrt(2 eps) (8.5).
5. P6 "new strays are an artefact": wrong (8.6).
6. "Seiferas's argument is potential-based": wrong; it is an invariant induction.
7. Round 2's "best derivable constant 1.9e5": artefact of a looser proof system.
8. L1's weight recursion and hence its reconstruction of 3.27 and its median formula: false as stated (3.2). New in this report.
9. P2's proof of adjacency of last-layer comparators: gap; statement is LIT (2.8). New in this report.
10. "Reduction to square merging" is folklore-level, not a discovery (5.5).

## 10. Open problems, sharpest forms

1. Square merger: M(k,k) = O(log k)? Small targets M(4,4) = 6, M(8,8) <= 13. Any gain must interleave sub-merging and cleanup (4.2).
2. D(2n) >= D(n) + 3, even for n = 16 (gives D(32) >= 12). Or a family theorem killing all layers 4-6 after a Green/hypercube start (needs a sound coupled relaxation).
3. Depth 13 at n = 32: outstanding SAT batches; greedy profile scores do not predict completability.
4. A correct statement and proof of the binomial-type weight lemma behind 3.27, then a "finishing lemma" with a richness condition (3.4).
5. A full proof of an AKS-type network in the retention or energy form with termination for all n, and an existence proof for block-sort separators (8.5, 8.8).
6. Is the 5.3 barrier tight: can rounds of depth O(log log n) contract G? Is there a constant-period network sorting in O(log n) rounds?
7. Novelty checks not done: Knuth 5.3.4 and Parberry for 2.1; Lee-Batcher's paper body for 4.3; the KLMPSS depth section for 3.


---

## Appendix A: builder for the 128- and 1024-wire networks (`build.py`)

```python
import json,sys
B16=[[(0,1),(2,3),(4,5),(6,7),(8,9),(10,11),(12,13),(14,15)],
[(0,2),(1,3),(4,6),(5,7),(8,10),(9,11),(12,14),(13,15)],
[(0,4),(1,5),(2,6),(3,7),(8,12),(9,13),(10,14),(11,15)],
[(0,8),(1,9),(2,10),(3,11),(4,12),(5,13),(6,14),(7,15)],
[(1,2),(3,12),(4,8),(5,10),(6,9),(7,11),(13,14)],
[(1,4),(2,8),(3,10),(5,9),(6,12),(7,13),(11,14)],
[(2,4),(3,8),(5,6),(7,9),(10,12),(11,13)],
[(3,5),(6,8),(7,10),(9,12)],
[(3,4),(5,6),(7,8),(9,10),(11,12)]]
def par(*nets):
    d=max(len(x) for x in nets); return [sum((x[i] for x in nets if i<len(x)),[]) for i in range(d)]
def kmerge(lists):
    L=len(lists[0]); k=len(lists)
    if L==2:
        w=[x for l in lists for x in l]
        return [[(w[a],w[b]) for a,b in lay] for lay in B16[1:]], w
    El,Eo=kmerge([l[0::2] for l in lists]); Ol,Oo=kmerge([l[1::2] for l in lists])
    out=[None]*(2*len(Eo)); out[0::2]=Eo; out[1::2]=Oo
    lays=par(El,Ol); s=1
    while s<k: s*=2
    s//=2
    while s>=1:
        lays.append([(out[2*i+1],out[2*i+2*s]) for i in range(len(out)//2) if 2*i+2*s<len(out)]); s//=2
    return lays,out
def sort16(w): return [[(w[a],w[b]) for a,b in lay] for lay in B16], list(w)
def sorter(w):
    n=len(w)
    if n==16: return sort16(w)
    sub=[sorter(w[i*n//8:(i+1)*n//8]) for i in range(8)]
    ml,out=kmerge([o for _,o in sub])
    return par(*[l for l,_ in sub])+ml,out
for n in (128,1024):
    lays,out=sorter(list(range(n)))
    pos={w:i for i,w in enumerate(out)}
    std=[[ (pos[a],pos[b]) for a,b in lay] for lay in lays]
    assert all(a<b for lay in std for a,b in lay)
    for lay in std:
        u=[x for c in lay for x in c]; assert len(u)==len(set(u))
    print(n,"depth",len(std),"size",sum(map(len,std)))
    json.dump({"n":n,"depth":len(std),"layers":std},open(f"net_{n}.json","w"))
```

## Appendix B: certificate checker (`verify.py`); usage `python3 verify.py net_1024.json`

```python
# Independent certificate checker: works only from the flat layer list, discovers the structure itself.
import json,sys,itertools,numpy as np
def comps_in(layers,a,b,W):
    out=[]
    for t in range(a,b):
        L=[]
        for x,y in layers[t]:
            ix,iy=x in W,y in W
            if ix!=iy: raise SystemExit(f"FAIL: comparator {(x,y)} in layer {t+1} leaves its wire group")
            if ix: L.append((x,y))
        out.append(L)
    return out
def components(cl,W):
    p={w:w for w in W}
    def f(x):
        while p[x]!=x: p[x]=p[p[x]]; x=p[x]
        return x
    for L in cl:
        for x,y in L: p[f(x)]=f(y)
    g={}
    for w in W: g.setdefault(f(w),[]).append(w)
    return [sorted(v) for v in g.values()]
def run(cl,ws,X):   # X: rows=inputs, cols=wires in label order ws
    idx={w:i for i,w in enumerate(ws)}
    for L in cl:
        for x,y in L:
            a,b=X[:,idx[x]].copy(),X[:,idx[y]].copy(); X[:,idx[x]]=a&b; X[:,idx[y]]=a|b
    return bool((X[:,:-1]<=X[:,1:]).all())
stats={"sort16":0,"base":0,"cleanup":0,"comps":0}
def sorter(layers,a,b,ws):
    W=set(ws); n=len(ws)
    if n==16:
        assert b-a==9; cl=comps_in(layers,a,b,W); stats["comps"]+=sum(map(len,cl))
        X=((np.arange(1<<16)[:,None]>>np.arange(16))&1).astype(np.uint8)
        if not run(cl,ws,X): raise SystemExit("FAIL: a 16-wire block does not sort")
        stats["sort16"]+=1; return
    ds={128:26,1024:26+0}[n] if n==128 else None
    dsub={128:9,1024:26}[n]
    groups=components(comps_in(layers,a,a+dsub,W),ws)
    if len(groups)!=8 or any(len(g)!=n//8 for g in groups): raise SystemExit("FAIL: block structure")
    for g in groups: sorter(layers,a,a+dsub,g)
    merger(layers,a+dsub,b,ws,groups)
def merger(layers,a,b,ws,lists):
    W=set(ws); k=len(lists); L=len(lists[0])
    if L==2:
        if b-a!=8: raise SystemExit("FAIL: base depth")
        cl=comps_in(layers,a,b,W); stats["comps"]+=sum(map(len,cl))
        rows=[]
        for z in itertools.product(range(3),repeat=k):
            v={}
            for l,zz in zip(lists,z): v[l[0]]=int(zz<1); v[l[1]]=int(zz<2)
            rows.append([v[w] for w in ws])
        if not run(cl,ws,np.array(rows,dtype=np.uint8)): raise SystemExit("FAIL: base merger of sorted pairs")
        stats["base"]+=1; return
    sub=comps_in(layers,a,b-3,W)
    parts=components(sub,ws)
    if len(parts)!=2: raise SystemExit(f"FAIL: expected 2 sub-mergers, found {len(parts)}")
    E,O=parts if lists[0][0] in parts[0] else parts[::-1]
    Es,Os=set(E),set(O)
    for l in lists:
        if any(w not in Es for w in l[0::2]) or any(w not in Os for w in l[1::2]): raise SystemExit("FAIL: even/odd split")
    merger(layers,a,b-3,E,[l[0::2] for l in lists]); merger(layers,a,b-3,O,[l[1::2] for l in lists])
    cl=comps_in(layers,b-3,b,W); stats["comps"]+=sum(map(len,cl))
    idx={w:i for i,w in enumerate(ws)}; ei=[idx[w] for w in E]; oi=[idx[w] for w in O]; h=len(E)
    rows=[]
    for ze in range(h+1):
        for zo in range(max(0,ze-k),ze+1):
            r=np.ones(len(ws),dtype=np.uint8); r[ei[:ze]]=0; r[oi[:zo]]=0; rows.append(r)
    if not run(cl,ws,np.array(rows)): raise SystemExit("FAIL: cleanup layers")
    stats["cleanup"]+=1
net=json.load(open(sys.argv[1])); layers=[[tuple(c) for c in L] for L in net["layers"]]; n=net["n"]
for L in layers:
    u=[x for c in L for x in c]; assert len(u)==len(set(u)) and all(x<y for x,y in L) and all(0<=x<n for x in u)
if len(sys.argv)>2:   # negative control: drop one comparator
    t,i=map(int,sys.argv[2:4]); print("dropping",layers[t].pop(i),"from layer",t+1)
sorter(layers,0,len(layers),list(range(n)))
tot=sum(map(len,layers))
print(f"n={n} depth={len(layers)} size={tot}: CERTIFIED. 16-sorters {stats['sort16']}, base mergers {stats['base']}, cleanup steps {stats['cleanup']}, comparators accounted {stats['comps']} of {tot}")
assert stats["comps"]==tot
```
