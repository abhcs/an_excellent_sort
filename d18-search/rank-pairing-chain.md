# Pairing-phase obstructions across arbitrarily many ranks

Suppose two layers remain. Let two wires have full four-rank intervals
[a,a+3] and [b,b+3], where b-a is odd and at least five. Suppose also that
for every k=a+3,...,b-2, some wire's attainable ranks contain the triple
[k,k+2]. Then there is no sorting completion.

The wires witnessing different triples need not be distinct. The
statement applies at arbitrary ambient width and makes no adjacency
assumption about the actual last matching.

## Hand proof

Consider only the two full intervals and the listed triples as required
sets. Any genuine ending supplies a last matching whose blocks meet each
required set at most twice. By the
[final-matching projection theorem](d13_feedback_round7_pairing.md), some
adjacent matching satisfies these requirements. Let e_i indicate its
edge(i,i+1).

The first full interval forces e_(a+2)=1, hence e_(a+3)=0. The second
forces e_b=1, hence e_(b-1)=0. Each required triple[k,k+2] forces exactly
one of e_k,e_(k+1) to be1: at least one to hit the triple, and at most one
because the edges share a vertex. Thus the variables from e_(a+3) through
e_(b-1) alternate. Their indices differ by b-a-4, which is odd, so their
values must differ. Both were forced to zero, a contradiction. □

The [three-rank bridge](d13_feedback_round7_bridge.md) is the special
case b=a+5. Longer chains detect incompatible pairing phases between
widely separated full cones, even though those cones have empty
intersection and do not themselves violate pairwise cone parity.
The compact path-variable formulation already propagates every such
chain; there is no need to enumerate all long chain clauses.

For even b-a, this local contradiction disappears: pairing consecutive
positions with the common phase supplies both full intervals and every
intervening triple. This is a control for the stated parity condition,
not a claim that a full prefix can then be completed.
