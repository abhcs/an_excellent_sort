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
static void rec(int k) {      /* k = index into order */
    if (k == n) { cnt++; mapset(cur); if (!have || lexless(cur, best)) { memcpy(best, cur, NW * sizeof(word)); have = 1; } return; }
    int c = order[k], cell = cellof[k];
    for (int p = cs[cell]; p < ce[cell]; p++) { if (usedpos[p]) continue; usedpos[p] = 1; perm[c] = p; rec(k + 1); usedpos[p] = 0; }
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

static word X3[NWW];
static long nstates; static Layer L4;
static uint32_t nonred[MAXN];
static void genL4(int c, uint32_t used) {
    while (c < n && (used >> c & 1)) c++;
    if (c == n) {
        word X4[NWW]; apply(X3, X4, &L4);
        if (nh == caph) { caph *= 2; hs = realloc(hs, caph * sizeof(H)); }
        canon(X4, &hs[nh++]); nstates++; return;
    }
    genL4(c + 1, used | 1u << c);                       /* c idle */
    for (int j = c + 1; j < n; j++) {
        if (used >> j & 1 || !(nonred[c] >> j & 1)) continue;
        L4.a[L4.m] = c; L4.b[L4.m] = j; L4.m++;
        genL4(c + 1, used | 1u << c | 1u << j);
        L4.m--;
    }
}
int main(int argc, char **argv) {
    int P; if (scanf("%d %d %d", &n, &A, &P) != 3) return 1;
    NW = (1 << n) / 64; FULL = (1u << n) - 1;
    caph = 1 << 22; hs = malloc(caph * sizeof(H));
    long prev_distinct = 0;
    for (int idx = 0; idx < P; idx++) {
        int p; if (scanf("%d", &p) != 1) return 1;
        word X[NWW]; memset(X, 0, sizeof X);
        for (uint32_t s = 0; s <= FULL; s++) X[s >> 6] |= 1ull << (s & 63);
        for (int l = 0; l < p; l++) { Layer L; if (scanf("%d", &L.m) != 1) return 1;
            for (int c = 0; c < L.m; c++) if (scanf("%d %d", &L.a[c], &L.b[c]) != 2) return 1;
            word Y[NWW]; apply(X, Y, &L); memcpy(X, Y, sizeof X); }
        memcpy(X3, X, sizeof X);
        memset(nonred, 0, sizeof nonred);
        for (int w = 0; w < NW; w++) { word v = X3[w]; while (v) { int b = __builtin_ctzll(v); v &= v - 1;
            uint32_t s = (uint32_t)(w * 64 + b), z = ~s & FULL;
            for (uint32_t o = s; o; o &= o - 1) nonred[__builtin_ctz(o)] |= z; } }
        L4.m = 0; genL4(0, 0);
        if ((idx + 1) % 100 == 0 || idx + 1 == P) {
            qsort(hs, nh, sizeof(H), cmpH);
            long w = 0; for (long i = 0; i < nh; i++) if (i == 0 || cmpH(&hs[i], &hs[w - 1])) hs[w++] = hs[i];
            nh = w;
            fprintf(stderr, "after %d prefixes: %ld fourth-layer states, %ld distinct classes\n", idx + 1, nstates, nh);
        }
    }
    printf("%d prefixes: %ld fourth-layer states, %ld distinct up to relabelling and complement\n", P, nstates, nh);
    return 0;
}
