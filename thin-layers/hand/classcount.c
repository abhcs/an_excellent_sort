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
static Layer L1, L3; static word X2[NWW];
static int np; static int pi_[80], pj_[80]; static long nprefix; static FILE *dumpf; static int cur_r;
static void genL3(int start, uint32_t used) {
    word X3[NWW]; apply(X2, X3, &L3);
    if (nh == caph) { caph *= 2; hs = realloc(hs, caph * sizeof(H)); }
    canon(X3, &hs[nh]);
    if (dumpf) { fprintf(dumpf, "%016llx%016llx %d", (unsigned long long)hs[nh].h1, (unsigned long long)hs[nh].h2, cur_r);
        for (int c = 0; c < L3.m; c++) fprintf(dumpf, " %d %d", L3.a[c], L3.b[c]); fprintf(dumpf, "\n"); }
    nh++; nprefix++;
    if (L3.m == A) return;
    for (int k = start; k < np; k++) { int i = pi_[k], j = pj_[k];
        if ((used >> i & 1) || (used >> j & 1)) continue;
        L3.a[L3.m] = i; L3.b[L3.m] = j; L3.m++;
        genL3(k + 1, used | 1u << i | 1u << j);
        L3.m--; }
}
int main(int argc, char **argv) {
    if (scanf("%d %d", &n, &A) != 2) return 1;
    NW = (1 << n) / 64; FULL = (1u << n) - 1;
    if (scanf("%d", &L1.m) != 1) return 1;
    for (int c = 0; c < L1.m; c++) if (scanf("%d %d", &L1.a[c], &L1.b[c]) != 2) return 1;
    int R; if (scanf("%d", &R) != 1) return 1;
    word X0[NWW], X1[NWW]; memset(X0, 0, sizeof X0);
    for (uint32_t s = 0; s <= FULL; s++) X0[s >> 6] |= 1ull << (s & 63);
    apply(X0, X1, &L1);
    caph = 1 << 20; hs = malloc(caph * sizeof(H));
    if (getenv("DUMP")) dumpf = fopen(getenv("DUMP"), "w");
    for (int r = 0; r < R; r++) {
        Layer L2; cur_r = r; if (scanf("%d", &L2.m) != 1) return 1;
        for (int c = 0; c < L2.m; c++) if (scanf("%d %d", &L2.a[c], &L2.b[c]) != 2) return 1;
        apply(X1, X2, &L2);
        np = 0;
        for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) {
            int nr = 0;
            for (int w = 0; w < NW && !nr; w++) { word v = X2[w]; while (v) { int b = __builtin_ctzll(v); v &= v - 1;
                uint32_t s = (uint32_t)(w * 64 + b); if ((s >> i & 1) && !(s >> j & 1)) { nr = 1; break; } } }
            if (nr) { pi_[np] = i; pj_[np] = j; np++; } }
        L3.m = 0; genL3(0, 0);
        if (r % 20 == 0) { fprintf(stderr, "L2 class %d: %ld prefixes so far\n", r, nprefix); }
    }
    if (dumpf) fclose(dumpf);
    qsort(hs, nh, sizeof(H), cmpH);
    long distinct = 0; for (long i = 0; i < nh; i++) if (i == 0 || cmpH(&hs[i], &hs[i - 1])) distinct++;
    printf("%ld prefixes, %ld reachable-set classes (relabelling + complement); permutations tried: max %ld, mean %.1f\n",
           nprefix, distinct, maxperm, (double)permsum / (2.0 * nprefix));
    if (argc > 1) { FILE *f = fopen(argv[1], "wb"); long k = 0; for (long i = 0; i < nh; i++) if (i == 0 || cmpH(&hs[i], &hs[i - 1])) { fwrite(&hs[i], sizeof(H), 1, f); k++; } fclose(f); }
    return 0;
}
