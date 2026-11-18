# An odd-idle obstruction closes third-layer form2

The three fixed layers are

    C = 01 23 45 | 02 15 36 | 12 34 78.

**Claim.** C cannot be followed by four sorting layers on nine wires.
This excludes third-layer form2 in the H9 class `02 15 36`, independently
of any restrictions already imposed on the fourth layer.

## 1. A local obstruction for an arbitrary next matching

Name the four remaining layers N,Q,P,S. Since N is a matching on nine
wires, it leaves some wire p idle. Fix that p. Write y for the output
of C on an input permutation of ranks0 through8. At the cut after N,
wire p still holds y_p. If another wire q is idle in N, it holds y_q;
if it is compared with r, it holds min(y_q,y_r) when q<r and
max(y_q,y_r) when q>r. Because p is idle, r cannot equal p.

If Q leaves p idle, the observed range of y_p has gap at least four,
as witnessed in the table below. If Q pairs p with q, exactly eight
local N modes at q are possible: idle, or pairing with any r outside
{p,q}. The table supplies a rank gap of at least four at the minimum
or maximum output of that Q comparison in every such mode.

For any actual comparator prefix, attainable ranks at a wire form an
interval. (Interchanging consecutive input ranks changes each output
rank by at most one; such swaps connect all input permutations.) Thus
each witnessed gap forces at least five attainable ranks at the chosen
Q output. Two remaining layers P,S can route that value to at most
four positions, a contradiction. Both the Q-idle and every Q-partner
option are impossible, so no such N,Q,P,S can exist.

Only the local N mode at q matters. Other N gates leave p and q's
comparator inputs untouched, and other Q gates leave the selected
Q output untouched. Consequently this proof covers all N and Q
matchings without enumerating either layer.

The argument generalizes to any odd width: a fixed finite input bank
that gives these local rank gaps at least as large as the remaining
forward-cone capacity excludes every pair of next matchings. Here the
capacity is four.

## 2. Eleven explicit input runs

The second column is on the original wires; the third is its output
after the three displayed layers C.

| Input | Original ranks | After C |
|---|---|---|
| A | `012345867` | `012345867` |
| B | `016723458` | `016243758` |
| C | `034567812` | `034567812` |
| D | `041256378` | `014256378` |
| E | `051267348` | `015267348` |
| F | `234567801` | `234567801` |
| G | `345607812` | `345067812` |
| H | `456701823` | `416075823` |
| I | `560178234` | `056178234` |
| J | `567801234` | `517026834` |
| K | `670128345` | `067128345` |

## 3. Guards covering every local N mode

In each row N leaves p idle. The Q entry is either idle or its partner q.
A guard `A–B/min {I,2,5}` says that the minimum Q output differs by at least4 between inputs A and B when q is idle in N (`I`) or has N partner2 or5. A max guard uses the maximum Q output. The N comparison itself always sends its minimum to the smaller-numbered wire.
For a Q-idle row, the guard directly compares y_p on the two inputs. For every other row the listed mode sets together contain I and all seven possible partners r outside {p,q}. There are9 idle cases and9*8*8=576 paired local cases.

| Idle N wire p | Q mode at p | Covering guards |
|---:|---|---|
| 0 | idle | A–H/idle {I} |
| 0 | 1 | A–J/max {I,2,3,4,5,6,7,8} |
| 0 | 2 | A–H/min {I,1,4,5,6}; B–C/max {7,8}; I–J/max {3,6} |
| 0 | 3 | A–H/min {2}; B–K/max {1}; I–J/max {I,4,5,6,7,8} |
| 0 | 4 | A–H/min {I,1,2,3,5,6}; C–D/max {7}; C–E/max {8} |
| 0 | 5 | A–C/max {7}; A–J/min {I,1,2,3,4,6,8} |
| 0 | 6 | A–C/max {7,8}; A–H/min {I,1,2,3,4,5} |
| 0 | 7 | A–H/min {2,4,5,6}; C–D/max {I,1,8}; D–G/max {I,3,8} |
| 0 | 8 | A–J/min {I,1,2,3,4,5,6,7} |
| 1 | idle | A–I/idle {I} |
| 1 | 0 | A–I/max {I,2,3,4,5,6,7,8} |
| 1 | 2 | A–K/max {I,0,3,4,5,6,7,8} |
| 1 | 3 | A–I/min {2}; B–K/max {I,0,4,5,6,7,8} |
| 1 | 4 | A–I/min {I,0,2,3,5}; J–K/max {I,3,5,6,7,8} |
| 1 | 5 | A–K/min {I,0,2,3,4,8}; B–C/max {I,0,3,6}; D–H/max {7} |
| 1 | 6 | A–D/max {I,0,2,3,8}; A–H/max {7,8}; A–I/min {2,4,5} |
| 1 | 7 | A–E/max {6}; A–H/max {I,3,8}; A–I/min {2,4,5}; C–D/max {I,0,8} |
| 1 | 8 | A–K/min {I,0,2,3,4,5,6,7} |
| 2 | idle | A–B/idle {I} |
| 2 | 0 | A–B/max {I,1,3,4,5,6,7,8} |
| 2 | 1 | A–B/max {I,0,3,4,5,6,7,8} |
| 2 | 3 | A–J/max {I,0,1,4,5,6,7,8} |
| 2 | 4 | A–H/min {I,0,1,3,6}; A–I/min {I,0,1,3,5}; E–F/min {7,8} |
| 2 | 5 | A–J/min {I,0,1,3,4,6}; E–F/min {7,8} |
| 2 | 6 | A–B/min {I,0,1,3,4,5,8}; B–C/min {7,8} |
| 2 | 7 | A–H/min {4,6}; A–K/min {1,5}; B–C/min {I,0,8}; B–G/min {I,3,8} |
| 2 | 8 | A–B/min {I,0,1,3,4,5,6,7} |
| 3 | idle | C–G/idle {I} |
| 3 | 0 | C–I/max {I,1,2,4,5,6,7,8} |
| 3 | 1 | B–K/max {I,0,2,5}; C–H/max {I,2,4,5,6,7,8} |
| 3 | 2 | B–G/max {7,8}; C–G/min {I,0,1,4,5,6} |
| 3 | 4 | C–G/min {I,0,1,2,5,6}; C–G/max {7}; E–G/max {8} |
| 3 | 5 | C–G/min {I,0,1,2,4,6}; D–G/max {6,7,8} |
| 3 | 6 | A–G/max {7,8}; C–G/min {I,0,1,2,4,5} |
| 3 | 7 | A–H/max {I,1,8}; C–G/min {2,4,5,6}; D–G/max {I,0,8} |
| 3 | 8 | B–G/max {I,0,1,7}; C–G/min {2,4,5,6} |
| 4 | idle | C–J/idle {I} |
| 4 | 0 | C–K/max {I,1,2,3,5,6,7,8} |
| 4 | 1 | A–I/min {I,0,2,5}; C–J/max {I,2,3,5,6,7,8} |
| 4 | 2 | A–I/min {I,0,1,5}; E–F/min {7,8}; H–K/max {3,6} |
| 4 | 3 | C–K/max {I,0,5,6,7,8}; I–J/min {1,2} |
| 4 | 5 | C–J/min {I,0,1,2,3,6}; D–F/min {7,8} |
| 4 | 6 | C–J/min {I,0,1,2,3,5}; H–K/max {I,0,3,7,8} |
| 4 | 7 | C–D/min {I,0,8}; C–J/min {5,6}; D–J/max {I,1,3,8}; H–J/min {2,6} |
| 4 | 8 | E–J/min {I,0,1,2,3,5,6,7} |
| 5 | idle | B–C/idle {I} |
| 5 | 0 | B–C/max {I,1,2,3,4,6,7,8} |
| 5 | 1 | B–C/max {I,0,2,3,4,6,7,8} |
| 5 | 2 | A–J/min {I,0,1,6}; B–I/max {3,4}; E–F/min {7,8} |
| 5 | 3 | A–K/min {2}; B–C/max {I,0,1,4,6,7,8} |
| 5 | 4 | B–I/min {I,0,1,2,3}; B–I/max {I,0,1,3,6,7,8} |
| 5 | 6 | A–F/min {7,8}; B–C/min {I,0,1,2,3,4} |
| 5 | 7 | A–C/min {I,0,8}; B–C/min {6}; B–I/min {4}; B–K/min {2}; D–H/min {I,1,3,8} |
| 5 | 8 | B–E/min {I,0,1,2,3,4,6,7} |
| 6 | idle | A–D/idle {I} |
| 6 | 0 | A–D/max {I,1,2,3,4,5,7,8} |
| 6 | 1 | A–D/max {I,0,2,3,4,5,7,8} |
| 6 | 2 | A–D/max {I,0,1,3,4,5,7,8} |
| 6 | 3 | A–D/max {I,0,1,2,4,5,7,8} |
| 6 | 4 | A–I/max {7,8}; C–I/min {I,0,1,2,3,5} |
| 6 | 5 | A–F/min {7,8}; C–D/min {I,0,1,2,3,4} |
| 6 | 7 | A–I/min {I,0,1,2,3,4,5,8} |
| 6 | 8 | A–D/min {I,0,1,2,3,4,5,7} |
| 7 | idle | A–C/idle {I} |
| 7 | 0 | A–C/max {I,1,2,3,4,5,6,8} |
| 7 | 1 | C–D/max {I,0,2,3,4,5,6,8} |
| 7 | 2 | D–F/min {I,0,1,4,5,8}; D–I/max {3,6} |
| 7 | 3 | D–G/max {I,0,4,5,6,8}; F–K/min {1,2} |
| 7 | 4 | A–F/min {I,0,1,2,3,5,6,8} |
| 7 | 5 | A–C/min {I,0,1,2,3,4,6,8} |
| 7 | 6 | A–C/min {I,0,1,2,3,4,5,8} |
| 7 | 8 | A–C/min {I,0,1,2,3,4,5,6} |
| 8 | idle | A–C/idle {I} |
| 8 | 0 | A–C/max {I,1,2,3,4,5,6,7} |
| 8 | 1 | A–C/max {I,0,2,3,4,5,6,7} |
| 8 | 2 | B–C/max {I,0,1,3,4,5,6,7} |
| 8 | 3 | B–C/min {2}; B–G/max {I,0,1,4,5,6,7} |
| 8 | 4 | B–I/max {6,7}; C–E/min {I,0,1,2,3,5} |
| 8 | 5 | A–F/min {I,0,1,2,3,4,6,7} |
| 8 | 6 | A–C/min {I,0,1,2,3,4,5,7} |
| 8 | 7 | A–C/min {I,0,1,2,3,4,5,6} |

## 4. Fixed verification

The [checker](verify/h9_recovery_021536_case2_check.py) evaluates only the eleven printed runs, validates all585 individual local witnesses and the140 covering guards, and checks complete local-mode coverage. It uses no SAT solver, input search, or matching enumeration.
The [certificate](results/h9-recovery-021536-case2-certificate.json) fixes the runs and guards; the [audit](results/h9-recovery-021536-case2-check.json) binds the checker and proof note.
