/* classcount.c -- how many reachable-set classes do the 3-layer sparse prefixes of T3(n, a) form?
 * (efficient-prefixes.md section 9).  Prefixes with the same reachable set after layer 3, up to a channel
 * relabelling and complement, need one token search between them (tokens depend only on that set).
 * Canonical form: channels sorted by invariants (per weight, how many reachable states have a 1 there; then
 * the multiset of pairwise co-occurrence vectors), minimum over the permutations inside equal cells, also for
 * the complemented set; a 128-bit hash of the canonical bitset is stored.
 * input: n a, L1 (m pairs), number of L2 reps, each rep (m pairs).  output: counts.
 * usage: classcount < spec.txt [hashes.bin] */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 12
#define NWW 64
typedef uint64_t word;
static int n, A, NW; static uint32_t FULL;
static int N0, NW0; static uint32_t FULL0;
typedef struct { int m; int a[MAXN], b[MAXN]; } Layer;
static void apply(const word *X, word *Y, const Layer *L) {
    memset(Y, 0, NW * sizeof(word));
    for (int w = 0; w < NW; w++) { word v = X[w]; while (v) { int b = __builtin_ctzll(v); v &= v - 1;
        uint32_t s = (uint32_t)(w * 64 + b);
        for (int c = 0; c < L->m; c++) { int i = L->a[c], j = L->b[c]; if ((s >> i & 1) && !(s >> j & 1)) s ^= (1u << i) | (1u << j); }
        Y[s >> 6] |= 1ull << (s & 63); } }
}
typedef struct { uint64_t h1, h2; } H;
static H *hs; static long nh, caph; static long maxperm, permsum;
static int cmpH(const void *a, const void *b) { const H *x = a, *y = b; if (x->h1 != y->h1) return x->h1 < y->h1 ? -1 : 1; if (x->h2 != y->h2) return x->h2 < y->h2 ? -1 : 1; return 0; }
/* canonical form of X */
static int inv1[MAXN][MAXN + 1];
static long key1[MAXN];
static word best[NWW], cur[NWW]; static int have;
static int perm[MAXN], cellof[MAXN], order[MAXN];
static const word *SRC;
static void mapset(word *out) {
    memset(out, 0, NW * sizeof(word));
    for (int w = 0; w < NW; w++) { word v = SRC[w]; while (v) { int b = __builtin_ctzll(v); v &= v - 1;
        uint32_t s = (uint32_t)(w * 64 + b), t = 0;
        for (int i = 0; i < n; i++) if (s >> i & 1) t |= 1u << perm[i];
        out[t >> 6] |= 1ull << (t & 63); } }
}
static int lexless(const word *x, const word *y) { for (int i = NW - 1; i >= 0; i--) if (x[i] != y[i]) return x[i] < y[i]; return 0; }
/* positions: cells are consecutive ranges of 'order'; assign perm[order[pos]] = pos within cell permutations */
static int cs[MAXN], ce[MAXN], ncell; static long cnt;
static int usedpos[MAXN];
static int prevsym[MAXN];   /* index (into order) of the previous member of k's symmetric block, or -1 */
static void rec(int k) {      /* k = index into order */
    if (k == n) { cnt++; mapset(cur); if (!have || lexless(cur, best)) { memcpy(best, cur, NW * sizeof(word)); have = 1; } return; }
    int c = order[k], cell = cellof[k];
    int lo = prevsym[k] >= 0 ? perm[order[prevsym[k]]] + 1 : cs[cell];   /* interchangeable channels: increasing positions */
    for (int p = lo; p < ce[cell]; p++) { if (usedpos[p]) continue; usedpos[p] = 1; perm[c] = p; rec(k + 1); usedpos[p] = 0; }
}
/* is SRC invariant under swapping channels i and j? */
static int swapsym(int i, int j) {
    for (int w = 0; w < NW; w++) { word v = SRC[w]; while (v) { int b = __builtin_ctzll(v); v &= v - 1;
        uint32_t s = (uint32_t)(w * 64 + b);
        if (((s >> i) & 1) != ((s >> j) & 1)) { uint32_t t = s ^ (1u << i) ^ (1u << j); if (!(SRC[t >> 6] >> (t & 63) & 1)) return 0; } } }
    return 1;
}
static void canon_one(const word *X) {
    SRC = X;
    for (int c = 0; c < n; c++) for (int w = 0; w <= n; w++) inv1[c][w] = 0;
    static int co[MAXN][MAXN];
    for (int c = 0; c < n; c++) for (int d = 0; d < n; d++) co[c][d] = 0;
    for (int w = 0; w < NW; w++) { word v = X[w]; while (v) { int b = __builtin_ctzll(v); v &= v - 1;
        uint32_t s = (uint32_t)(w * 64 + b); int wt = __builtin_popcount(s);
        for (uint32_t o = s; o; o &= o - 1) { int c = __builtin_ctz(o); inv1[c][wt]++;
            for (uint32_t o2 = s; o2; o2 &= o2 - 1) co[c][__builtin_ctz(o2)] += 1 + wt; } } }
    /* key per channel: hash of inv1 row and the sorted co-occurrence row */
    for (int c = 0; c < n; c++) { uint64_t h = 1469598103934665603ull;
        for (int w = 0; w <= n; w++) { h ^= (uint64_t)inv1[c][w]; h *= 1099511628211ull; }
        int row[MAXN]; for (int d = 0; d < n; d++) row[d] = co[c][d];
        for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (row[j] < row[i]) { int t = row[i]; row[i] = row[j]; row[j] = t; }
        for (int d = 0; d < n; d++) { h ^= (uint64_t)row[d]; h *= 1099511628211ull; }
        key1[c] = (long)(h >> 1); }
    for (int i = 0; i < n; i++) order[i] = i;
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (key1[order[j]] < key1[order[i]]) { int t = order[i]; order[i] = order[j]; order[j] = t; }
    ncell = 0;
    for (int i = 0; i < n; ) { int j = i; while (j < n && key1[order[j]] == key1[order[i]]) j++; cs[ncell] = i; ce[ncell] = j; for (int k = i; k < j; k++) cellof[k] = ncell; ncell++; i = j; }
    /* symmetric blocks inside each cell: channels whose transposition leaves the set invariant */
    for (int k = 0; k < n; k++) { prevsym[k] = -1;
        for (int k2 = k - 1; k2 >= cs[cellof[k]]; k2--) if (swapsym(order[k], order[k2])) { prevsym[k] = k2; break; } }
    memset(usedpos, 0, sizeof usedpos); cnt = 0;
    rec(0);
    if (cnt > maxperm) maxperm = cnt; permsum += cnt;
}
static void canon(const word *X, H *out) {
    word C[NWW]; memset(C, 0, sizeof C);
    for (int w = 0; w < NW; w++) { word v = X[w]; while (v) { int b = __builtin_ctzll(v); v &= v - 1;
        uint32_t s = ((uint32_t)(w * 64 + b)) ^ FULL; C[s >> 6] |= 1ull << (s & 63); } }
    word b1[NWW]; have = 0; canon_one(X); memcpy(b1, best, NW * sizeof(word));
    const word *m = b1;
    if (!getenv("NOCOMP")) { have = 0; canon_one(C); m = lexless(best, b1) ? best : b1; }
    uint64_t h1 = 1469598103934665603ull, h2 = 0x9e3779b97f4a7c15ull;
    for (int i = 0; i < NW; i++) { h1 ^= m[i]; h1 *= 1099511628211ull; h2 += m[i] * 0xbf58476d1ce4e5b9ull; h2 ^= h2 >> 31; }
    out->h1 = h1; out->h2 = h2;
}

/* resid: for every 3-layer prefix of T3(n, a) (same order as classcount), the classes of the residual
 * (n-1)-channel prefixes under a sentinel (+inf on input s: inputs with x_s = 1; -inf: x_s = 0), the sentinel's
 * channel deleted after layer 3.  Writes per prefix-class (n-channel hash) the distinct residual-class hashes.
 * GOOD=1: only sentinels on L1 comparator ends whose track meets every full layer (the descent's good tracks);
 * otherwise all 2n sentinels. */
static Layer L1, L2c, L3; static word X1[NWW], X2[NWW];
static int np; static int pi_[80], pj_[80]; static long nprefix; static int good_only;
typedef struct { uint64_t k1, k2; int n10; int cap; uint64_t (*h10)[2]; } Ent;
static Ent *tab; static long tabcap, tabn;
static Ent *get(uint64_t k1, uint64_t k2) {
    long i = (long)(k1 % (uint64_t)tabcap);
    while (tab[i].cap && !(tab[i].k1 == k1 && tab[i].k2 == k2)) i = (i + 1) % tabcap;
    if (!tab[i].cap) { tab[i].k1 = k1; tab[i].k2 = k2; tab[i].cap = 4; tab[i].n10 = 0; tab[i].h10 = malloc(4 * 16); tabn++; }
    return &tab[i];
}
static void addh(Ent *e, uint64_t a, uint64_t b) {
    for (int i = 0; i < e->n10; i++) if (e->h10[i][0] == a && e->h10[i][1] == b) return;
    if (e->n10 == e->cap) { e->cap *= 2; e->h10 = realloc(e->h10, e->cap * 16); }
    e->h10[e->n10][0] = a; e->h10[e->n10][1] = b; e->n10++;
}
static const Layer *LAY[3];
static int track_end(int s, int plus, int *good) {
    int pos = s; *good = 1;
    for (int l = 0; l < 3; l++) { const Layer *L = LAY[l]; int met = 0;
        for (int c = 0; c < L->m; c++) { if (L->a[c] == pos || L->b[c] == pos) { met = 1; pos = plus ? L->b[c] : L->a[c]; break; } }
        if (!met && L->m == A) *good = 0;
        if (l == 0 && !met) *good = 0; }
    return pos;
}
static long nres, nresgood;
static void process_prefix(void) {
    word X3[NWW]; apply(X2, X3, &L3);
    H h; int saveN = n, saveNW = NW; uint32_t saveF = FULL;
    canon(X3, &h);
    Ent *e = get(h.h1, h.h2);
    LAY[0] = &L1; LAY[1] = &L2c; LAY[2] = &L3;
    for (int s = 0; s < N0; s++) for (int plus = 0; plus < 2; plus++) {
        int good; int p = track_end(s, plus, &good);
        if (good_only && !good) continue;
        /* residual set: images of inputs with x_s = plus, bit p deleted */
        word R[NWW]; memset(R, 0, sizeof R);
        for (uint32_t x = 0; x <= FULL0; x++) {
            if (((x >> s) & 1) != (uint32_t)plus) continue;
            uint32_t t = x;
            for (int l = 0; l < 3; l++) { const Layer *L = LAY[l];
                for (int c = 0; c < L->m; c++) { int i = L->a[c], j = L->b[c]; if ((t >> i & 1) && !(t >> j & 1)) t ^= (1u << i) | (1u << j); } }
            uint32_t lowm = (1u << p) - 1; uint32_t r = (t & lowm) | ((t >> (p + 1)) << p);
            R[r >> 6] |= 1ull << (r & 63);
        }
        n = N0 - 1; NW = (1 << n) / 64; if (NW < 1) NW = 1; FULL = (1u << n) - 1;
        H hr; canon(R, &hr);
        n = saveN; NW = saveNW; FULL = saveF;
        addh(e, hr.h1, hr.h2); nres++; nresgood += good;
    }
    nprefix++;
}
static void genL3(int start, uint32_t used) {
    process_prefix();
    if (L3.m == A) return;
    for (int k = start; k < np; k++) { int i = pi_[k], j = pj_[k];
        if ((used >> i & 1) || (used >> j & 1)) continue;
        L3.a[L3.m] = i; L3.b[L3.m] = j; L3.m++;
        genL3(k + 1, used | 1u << i | 1u << j);
        L3.m--; }
}
int main(int argc, char **argv) {
    good_only = getenv("GOOD") && getenv("GOOD")[0] == '1';
    if (scanf("%d %d", &n, &A) != 2) return 1;
    N0 = n; NW = (1 << n) / 64; FULL = (1u << n) - 1; NW0 = NW; FULL0 = FULL;
    if (scanf("%d", &L1.m) != 1) return 1;
    for (int c = 0; c < L1.m; c++) if (scanf("%d %d", &L1.a[c], &L1.b[c]) != 2) return 1;
    int Rn; if (scanf("%d", &Rn) != 1) return 1;
    word X0[NWW]; memset(X0, 0, sizeof X0);
    for (uint32_t s = 0; s <= FULL; s++) X0[s >> 6] |= 1ull << (s & 63);
    apply(X0, X1, &L1);
    tabcap = 1 << 21; tab = calloc(tabcap, sizeof(Ent));
    for (int r = 0; r < Rn; r++) {
        if (scanf("%d", &L2c.m) != 1) return 1;
        for (int c = 0; c < L2c.m; c++) if (scanf("%d %d", &L2c.a[c], &L2c.b[c]) != 2) return 1;
        apply(X1, X2, &L2c);
        np = 0;
        for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) {
            int nr = 0;
            for (int w = 0; w < NW && !nr; w++) { word v = X2[w]; while (v) { int b = __builtin_ctzll(v); v &= v - 1;
                uint32_t s = (uint32_t)(w * 64 + b); if ((s >> i & 1) && !(s >> j & 1)) { nr = 1; break; } } }
            if (nr) { pi_[np] = i; pj_[np] = j; np++; } }
        L3.m = 0; genL3(0, 0);
        if (r % 20 == 0) fprintf(stderr, "L2 class %d: %ld prefixes, %ld prefix classes so far\n", r, nprefix, tabn);
    }
    FILE *f = fopen(argv[1], "w"); long tot = 0;
    for (long i = 0; i < tabcap; i++) if (tab[i].cap) {
        fprintf(f, "%016llx%016llx", (unsigned long long)tab[i].k1, (unsigned long long)tab[i].k2);
        for (int k = 0; k < tab[i].n10; k++) fprintf(f, " %016llx%016llx", (unsigned long long)tab[i].h10[k][0], (unsigned long long)tab[i].h10[k][1]);
        fprintf(f, "\n"); tot += tab[i].n10; }
    fclose(f);
    printf("%ld prefixes, %ld prefix classes, %ld residuals computed (%ld on good tracks), %ld distinct (class, residual class) pairs\n",
           nprefix, tabn, nres, nresgood, tot);
    return 0;
}
