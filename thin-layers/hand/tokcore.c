/* tokcore.c -- complete search for sorting networks below a fixed prefix, pruned only by probe
 * tokens and cone bounds (h9.md Lemma 13, efficient-prefixes.md §3).  It measures how much of a
 * case the token argument alone settles.
 *
 * A probe after layer t is a pair of reachable states s, s + e_j; its token (channel j) must end
 * on output k = n-1-|s|.  T_t(k) = channels holding some token for k, read directly from the
 * reachable set X_t.  In normal form the last layer is adjacent and the penultimate one has
 * comparators of length <= 3, so in a depth-D sorter
 *     |T_t(k)| <= 2^(D-t),   T_D(k) = {k},   T_{D-1}(k) within k +- 1,   T_{D-2}(k) within k +- 4.
 * The next layer is chosen channel by channel; the images of the current tokens (a token goes to
 * the high end of its comparator if the other channel holds 0, else to the low end) must already
 * meet these bounds.  Every comparator is non-redundant (swaps on some reachable state).
 *
 * input (stdin):  n D P, then P prefixes: p, then p layers "m i1 j1 ... im jm"
 * output: per prefix "idx nodes_1 ... nodes_D found", nodes_t = layer-t choices (t > p) that pass.
 * usage: tokcore [MAXNODES]   (stops a prefix after MAXNODES nodes; 0 = no limit)
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 16
#define MAXD 16
typedef uint64_t word;

static int n, D, NW;
static uint32_t FULL;
static long long nodes[MAXD + 1], maxnodes, total;
static int found, stopped;
static int bound[MAXD + 1];
static uint32_t OUTMASK = 0xffffffffu;
static int POS = 1;
static uint32_t allowed[MAXD + 1][MAXN];

typedef struct { int m; int a[MAXN / 2], b[MAXN / 2]; } Layer;
typedef struct {
    uint32_t T[MAXN];          /* token channels of output k */
    uint32_t s0[MAXN][MAXN];   /* s0[k][j]: channels o seen as 0 by some token of k on j */
    uint32_t s1[MAXN][MAXN];
    uint32_t nonred[MAXN];     /* nonred[i]: channels j such that some state has 1 on i, 0 on j */
} Tok;

static inline int has(const word *X, uint32_t s) { return (int)(X[s >> 6] >> (s & 63) & 1); }

static void apply_layer(const word *X, word *Y, const Layer *L) {
    memset(Y, 0, NW * sizeof(word));
    for (int w = 0; w < NW; w++) {
        word v = X[w];
        while (v) {
            int b = __builtin_ctzll(v);
            v &= v - 1;
            uint32_t s = (uint32_t)(w * 64 + b);
            for (int c = 0; c < L->m; c++) {
                int i = L->a[c], j = L->b[c];
                if ((s >> i & 1) && !(s >> j & 1)) s ^= (1u << i) | (1u << j);
            }
            Y[s >> 6] |= 1ull << (s & 63);
        }
    }
}

static void tokens(const word *X, Tok *t) {
    memset(t, 0, sizeof *t);
    for (int w = 0; w < NW; w++) {
        word v = X[w];
        while (v) {
            int b = __builtin_ctzll(v);
            v &= v - 1;
            uint32_t s = (uint32_t)(w * 64 + b);
            uint32_t zeros = ~s & FULL;
            for (uint32_t ones = s; ones; ones &= ones - 1) t->nonred[__builtin_ctz(ones)] |= zeros;
            int k = n - 1 - __builtin_popcount(s);
            for (uint32_t z = zeros; z; z &= z - 1) {
                int j = __builtin_ctz(z);
                if (has(X, s | 1u << j)) {
                    t->T[k] |= 1u << j;
                    t->s0[k][j] |= zeros & ~(1u << j);
                    t->s1[k][j] |= s;
                }
            }
        }
    }
}

static int tokens_ok(const Tok *t, int lev) {
    for (int k = 0; k < n; k++) {
        if ((OUTMASK >> k & 1) && __builtin_popcount(t->T[k]) > bound[lev]) return 0;
        if (t->T[k] & ~allowed[lev][k]) return 0;
    }
    return 1;
}

static void search(int t, const word *X);

/* choose layer t+1 channel by channel; U[k] = images of the tokens of k so far */
static void rec(int t, const word *X, const Tok *tk, Layer *L, uint32_t used, const uint32_t *U) {
    if (stopped) return;
    int c = 0;
    while (c < n && (used >> c & 1)) c++;
    uint32_t V[MAXN];
    int lev = t + 1;
    if (c == n) {
        word Y[1024];
        apply_layer(X, Y, L);
        Tok t2;
        tokens(Y, &t2);
        if (!tokens_ok(&t2, lev)) return;
        nodes[lev]++;
        if (maxnodes && ++total > maxnodes) { stopped = 1; return; }
        if (lev == D) {
            for (int k = 0; k < n; k++) if (t2.T[k] & ~(1u << k)) return;   /* sorted? */
            found = 1; stopped = 1; return;
        }
        search(lev, Y);
        return;
    }
    /* c idle */
    int ok = 1;
    for (int k = 0; k < n && ok; k++) {
        V[k] = U[k] | (tk->T[k] & 1u << c);
        if (((OUTMASK >> k & 1) && __builtin_popcount(V[k]) > bound[lev]) || (V[k] & ~allowed[lev][k])) ok = 0;
    }
    if (ok) rec(t, X, tk, L, used | 1u << c, V);
    /* c paired with a later free channel j: comparator (c, j), max to j */
    for (int j = c + 1; j < n; j++) {
        if (used >> j & 1) continue;
        if (!(tk->nonred[c] >> j & 1)) continue;          /* redundant comparator */
        ok = 1;
        for (int k = 0; k < n && ok; k++) {
            uint32_t img = 0;
            if (((tk->s0[k][c] >> j) | (tk->s0[k][j] >> c)) & 1) img |= 1u << j;
            if (((tk->s1[k][c] >> j) | (tk->s1[k][j] >> c)) & 1) img |= 1u << c;
            V[k] = U[k] | img;
            if (((OUTMASK >> k & 1) && __builtin_popcount(V[k]) > bound[lev]) || (V[k] & ~allowed[lev][k])) ok = 0;
        }
        if (!ok) continue;
        L->a[L->m] = c;
        L->b[L->m] = j;
        L->m++;
        rec(t, X, tk, L, used | 1u << c | 1u << j, V);
        L->m--;
        if (stopped) return;
    }
}

static void search(int t, const word *X) {
    if (t >= D || stopped) return;
    Tok tk;
    tokens(X, &tk);
    Layer L;
    L.m = 0;
    uint32_t U[MAXN] = {0};
    rec(t, X, &tk, &L, 0, U);
}

int main(int argc, char **argv) {
    maxnodes = argc > 1 ? atoll(argv[1]) : 0;
    if (argc > 2) OUTMASK = (uint32_t)strtoul(argv[2], 0, 16);
    if (argc > 3) POS = atoi(argv[3]);
    int P;
    if (scanf("%d %d %d", &n, &D, &P) != 3) return 1;
    NW = (1 << n) / 64;
    if (NW < 1) NW = 1;
    FULL = (n == 32) ? 0xffffffffu : ((1u << n) - 1);
    for (int t = 0; t <= D; t++) {
        int r = D - t;
        bound[t] = r >= 5 ? n : (1 << r);
        if (bound[t] > n) bound[t] = n;
        for (int k = 0; k < n; k++) {
            int w = r == 0 ? 0 : r == 1 ? 1 : r == 2 ? 4 : n;
            uint32_t m = 0;
            for (int c = 0; c < n; c++)
                if (c >= k - w && c <= k + w) m |= 1u << c;
            allowed[t][k] = POS ? m : FULL;
        }
    }
    for (int t = 0; t <= D; t++)
        for (int k = 0; k < n; k++)
            if (!(OUTMASK >> k & 1)) allowed[t][k] = FULL;
    for (int idx = 0; idx < P; idx++) {
        int p;
        if (scanf("%d", &p) != 1) return 1;
        word X[1024];
        memset(X, 0, sizeof X);
        for (uint32_t s = 0; s < (1u << n); s++) X[s >> 6] |= 1ull << (s & 63);
        const char *se = getenv("TOK_STATIC"); int stat = se && se[0] == '1';
        int ra[64], rb[64], nr = 0;
        for (int l = 0; l < p; l++) {
            Layer L;
            if (scanf("%d", &L.m) != 1) return 1;
            for (int c = 0; c < L.m; c++) {
                if (scanf("%d %d", &L.a[c], &L.b[c]) != 2) return 1;
                ra[nr] = L.a[c]; rb[nr] = L.b[c]; nr++;
            }
            if (!stat) {
                word Y[1024];
                apply_layer(X, Y, &L);
                memcpy(X, Y, NW * sizeof(word));
            }
        }
        if (stat) {
            memset(X, 0, sizeof X);
            for (uint32_t s = 0; s < (1u << n); s++) {
                int ok = 1;
                for (int r = 0; r < nr && ok; r++) if ((s >> ra[r] & 1) && !(s >> rb[r] & 1)) ok = 0;
                if (ok) X[s >> 6] |= 1ull << (s & 63);
            }
        }
        memset(nodes, 0, sizeof nodes);
        found = stopped = 0;
        total = 0;
        search(p, X);
        printf("%d", idx);
        for (int t = p + 1; t <= D; t++) printf(" %lld", nodes[t]);
        printf(" %s\n", found ? "FOUND" : (stopped ? "LIMIT" : "none"));
        fflush(stdout);
    }
    return 0;
}
