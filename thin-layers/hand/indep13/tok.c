/* indep13/tok.c -- independent token refuter for the D(13) proof (efficient-prefixes.md section 9.1).
 *
 * Written from the definitions, without code from tokcore.c or tokcore2.c, and using fewer facts than
 * they do (no normal form of the last layers, no merge-matching filter):
 *  1. Rank intervals (section 5, Lemma 2).  After t layers let S_t be the image of all 0-1 inputs;
 *     comparators keep the weight |u|.  Channel c can hold the element of rank k (0 = least) for some
 *     input permutation iff lo_c <= k <= hi_c, where
 *         lo_c = n-1 - max{|u| : u in S_t, u_c = 0},   hi_c = n - min{|u| : u in S_t, u_c = 1}.
 *     T_t(k) = {c : lo_c <= k <= hi_c}.
 *  2. Cone bound.  In a depth-D sorter the element of rank k ends on channel k.  After layer t it can
 *     only be on a channel from which channel k is reachable through layers t+1..D, and there are at
 *     most 2^(D-t) of those.  So |T_t(k)| <= 2^(D-t).
 *  3. A comparator that swaps no state of S_t can be deleted from layer t+1 without changing S_{t+1},
 *     so only comparators that swap some state are tried.
 * A comparator (i, j), i < j, min to i, replaces the channel functions f_i, f_j by f_i AND f_j on i and
 * f_i OR f_j on j, so the two new intervals follow from S_t alone:
 *     on i: [min(lo_i, lo_j), n - min{|u| : u_i = u_j = 1}],
 *     on j: [n-1 - max{|u| : u_i = u_j = 0}, max(hi_i, hi_j)];
 * an idle channel keeps its interval.
 * Search: every layer from p+1 on that meets the bound of its layer; at layer D the network must sort.
 * Each layer is chosen channel by channel (the least unassigned channel idles or takes a partner).  A
 * partial layer is cut when some rank is covered by more channels than the bound allows, counting the
 * channels already assigned and every unassigned channel whose options all cover that rank.
 * The search stops at the first sorter.  A prefix is refuted when the whole search finds none.
 *
 * input (stdin), one prefix per line:  idx n D p  then p layers, each "m i1 j1 ... im jm"
 * output, one line per prefix:  idx nodes_{p+1} ... nodes_D outcome seconds
 *   nodes_t = complete layers t that meet the bound; outcome = refuted | SORTER (then the sorter's layers)
 * usage: tok < prefixes.txt > results.txt
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXN 12
#define MAXD 16
#define MAXWORDS (1 << (MAXN - 6))
typedef uint64_t u64;

static int n, D, NW;
static uint32_t ALL;
static long long nodes[MAXD + 1];
static int found;
static int lay_m[MAXD + 1], lay_a[MAXD + 1][MAXN], lay_b[MAXD + 1][MAXN];   /* current layers */
static int got_m[MAXD + 1], got_a[MAXD + 1][MAXN], got_b[MAXD + 1][MAXN];   /* the sorter found */

typedef struct {
    int lo[MAXN], hi[MAXN];               /* intervals after layer t */
    int nlo[MAXN][MAXN], nhi[MAXN][MAXN]; /* [x][y]: interval of x after a comparator on (x, y) */
    uint32_t swaps[MAXN];                 /* bit j of swaps[i] (j > i): (i, j) swaps some state */
} Info;

static void info(const u64 *S, Info *I) {
    int m1[MAXN], M0[MAXN];
    uint32_t one[MAXN + 1][MAXN], zero[MAXN + 1][MAXN], sw[MAXN];
    memset(one, 0, sizeof one);
    memset(zero, 0, sizeof zero);
    for (int c = 0; c < n; c++) { m1[c] = n + 1; M0[c] = -1; sw[c] = 0; }
    for (int w = 0; w < NW; w++) {
        u64 v = S[w];
        while (v) {
            uint32_t u = (uint32_t)(w * 64 + __builtin_ctzll(v));
            v &= v - 1;
            int k = __builtin_popcount(u);
            uint32_t z = ~u & ALL;
            for (uint32_t b = u; b; b &= b - 1) {
                int c = __builtin_ctz(b);
                if (k < m1[c]) m1[c] = k;
                one[k][c] |= u;     /* channels that are 1 together with c in some state of weight k */
                sw[c] |= z;         /* channels that are 0 while c is 1 */
            }
            for (uint32_t b = z; b; b &= b - 1) {
                int c = __builtin_ctz(b);
                if (k > M0[c]) M0[c] = k;
                zero[k][c] |= z;    /* channels that are 0 together with c in some state of weight k */
            }
        }
    }
    for (int c = 0; c < n; c++) {
        if (m1[c] > n || M0[c] < 0) { fprintf(stderr, "set misses 0...0 or 1...1\n"); exit(2); }
        I->lo[c] = n - 1 - M0[c];
        I->hi[c] = n - m1[c];
    }
    for (int i = 0; i < n; i++) {
        int both1[MAXN], both0[MAXN];
        uint32_t seen = 0;
        for (int k = 0; k <= n; k++) {          /* least weight with u_i = u_j = 1 */
            uint32_t nw = one[k][i] & ~seen;
            seen |= nw;
            for (; nw; nw &= nw - 1) both1[__builtin_ctz(nw)] = k;
        }
        seen = 0;
        for (int k = n; k >= 0; k--) {          /* largest weight with u_i = u_j = 0 */
            uint32_t nw = zero[k][i] & ~seen;
            seen |= nw;
            for (; nw; nw &= nw - 1) both0[__builtin_ctz(nw)] = k;
        }
        for (int j = i + 1; j < n; j++) {
            I->nlo[i][j] = I->lo[i] < I->lo[j] ? I->lo[i] : I->lo[j];
            I->nhi[i][j] = n - both1[j];
            I->nlo[j][i] = n - 1 - both0[j];
            I->nhi[j][i] = I->hi[i] > I->hi[j] ? I->hi[i] : I->hi[j];
        }
        I->swaps[i] = sw[i] & ~((2u << i) - 1u);
    }
}

static void apply(const u64 *S, u64 *T, int m, const int *a, const int *b) {
    memset(T, 0, NW * sizeof(u64));
    for (int w = 0; w < NW; w++) {
        u64 v = S[w];
        while (v) {
            uint32_t u = (uint32_t)(w * 64 + __builtin_ctzll(v));
            v &= v - 1;
            for (int c = 0; c < m; c++)
                if ((u >> a[c] & 1) && !(u >> b[c] & 1)) u ^= (1u << a[c]) | (1u << b[c]);
            T[u >> 6] |= 1ull << (u & 63);
        }
    }
}

static int sorts(const u64 *S) {
    for (int w = 0; w < NW; w++) {
        u64 v = S[w];
        while (v) {
            uint32_t u = (uint32_t)(w * 64 + __builtin_ctzll(v));
            v &= v - 1;
            int k = __builtin_popcount(u);
            if (u != (ALL & ~((1u << (n - k)) - 1u))) return 0;   /* the k ones must be on the top k channels */
        }
    }
    return 1;
}

static int bound(int t) { int r = D - t; return r >= 5 ? n : ((1 << r) < n ? (1 << r) : n); }

static void search(int t, const u64 *S);

typedef struct {
    int t, B;
    const u64 *S;
    const Info *I;
    int flo[MAXN], fhi[MAXN];   /* forced interval of each channel: common to all its options */
    int tot[MAXN + 1];          /* per rank: assigned channels covering it + unassigned forced ones */
} Build;

/* channel c leaves the unassigned pool and takes interval [a, b]; returns 0 if a rank exceeds B */
static int place(Build *z, int c, int a, int b) {
    for (int k = z->flo[c]; k <= z->fhi[c]; k++) z->tot[k]--;
    int ok = 1;
    for (int k = a; k <= b; k++) if (++z->tot[k] > z->B) ok = 0;
    return ok;
}
static void unplace(Build *z, int c, int a, int b) {
    for (int k = a; k <= b; k++) z->tot[k]--;
    for (int k = z->flo[c]; k <= z->fhi[c]; k++) z->tot[k]++;
}

static void complete(Build *z) {
    int t1 = z->t + 1;
    nodes[t1]++;
    u64 T[MAXWORDS];
    apply(z->S, T, lay_m[t1], lay_a[t1], lay_b[t1]);
    if (t1 == D) {
        if (sorts(T)) {
            found = 1;
            memcpy(got_m, lay_m, sizeof got_m); memcpy(got_a, lay_a, sizeof got_a); memcpy(got_b, lay_b, sizeof got_b);
        }
        return;
    }
    search(t1, T);
}

static void build(Build *z, uint32_t pool) {
    if (found) return;
    if (!pool) { complete(z); return; }
    const Info *I = z->I;
    int c = __builtin_ctz(pool), t1 = z->t + 1;
    uint32_t rest = pool & ~(1u << c);
    if (place(z, c, I->lo[c], I->hi[c])) build(z, rest);          /* c idle */
    unplace(z, c, I->lo[c], I->hi[c]);
    for (uint32_t cand = I->swaps[c] & rest; cand && !found; cand &= cand - 1) {
        int d = __builtin_ctz(cand);
        int okc = place(z, c, I->nlo[c][d], I->nhi[c][d]);
        int okd = place(z, d, I->nlo[d][c], I->nhi[d][c]);
        if (okc && okd) {
            int m = lay_m[t1]++;
            lay_a[t1][m] = c; lay_b[t1][m] = d;
            build(z, rest & ~(1u << d));
            lay_m[t1]--;
        }
        unplace(z, d, I->nlo[d][c], I->nhi[d][c]);
        unplace(z, c, I->nlo[c][d], I->nhi[c][d]);
    }
}

static void search(int t, const u64 *S) {
    Info I;
    info(S, &I);
    Build z;
    z.t = t; z.B = bound(t + 1); z.S = S; z.I = &I;
    memset(z.tot, 0, sizeof z.tot);
    for (int c = 0; c < n; c++) {
        int a = I.lo[c], b = I.hi[c];
        for (int d = c + 1; d < n; d++) if (I.swaps[c] >> d & 1) {
            if (I.nlo[c][d] > a) a = I.nlo[c][d];
            if (I.nhi[c][d] < b) b = I.nhi[c][d];
        }
        for (int e = 0; e < c; e++) if (I.swaps[e] >> c & 1) {
            if (I.nlo[c][e] > a) a = I.nlo[c][e];
            if (I.nhi[c][e] < b) b = I.nhi[c][e];
        }
        z.flo[c] = a; z.fhi[c] = b;           /* empty when a > b */
        for (int k = a; k <= b; k++) z.tot[k]++;
    }
    for (int k = 0; k < n; k++) if (z.tot[k] > z.B) return;
    lay_m[t + 1] = 0;
    build(&z, ALL);
}

int main(void) {
    int idx, p;
    while (scanf("%d %d %d %d", &idx, &n, &D, &p) == 4) {
        if (n < 2 || n > MAXN || D > MAXD || p > D) { fprintf(stderr, "bad header\n"); return 1; }
        NW = n >= 6 ? (1 << n) / 64 : 1;
        ALL = (1u << n) - 1u;
        int m[MAXD + 1], a[MAXD + 1][MAXN], b[MAXD + 1][MAXN];
        for (int l = 0; l < p; l++) {
            if (scanf("%d", &m[l]) != 1) return 1;
            for (int c = 0; c < m[l]; c++) {
                if (scanf("%d %d", &a[l][c], &b[l][c]) != 2) return 1;
                if (!(0 <= a[l][c] && a[l][c] < b[l][c] && b[l][c] < n)) { fprintf(stderr, "bad comparator\n"); return 1; }
            }
        }
        clock_t t0 = clock();
        u64 S[MAXWORDS];
        memset(S, 0, sizeof S);
        for (uint32_t x = 0; x <= ALL; x++) {
            uint32_t u = x;
            for (int l = 0; l < p; l++)
                for (int c = 0; c < m[l]; c++)
                    if ((u >> a[l][c] & 1) && !(u >> b[l][c] & 1)) u ^= (1u << a[l][c]) | (1u << b[l][c]);
            S[u >> 6] |= 1ull << (u & 63);
        }
        memset(nodes, 0, sizeof nodes);
        found = 0;
        search(p, S);
        printf("%d", idx);
        for (int t = p + 1; t <= D; t++) printf(" %lld", nodes[t]);
        if (found) {
            printf(" SORTER");
            for (int t = p + 1; t <= D; t++) {
                printf(" |");
                for (int c = 0; c < got_m[t]; c++) printf(" %d %d", got_a[t][c], got_b[t][c]);
            }
        } else printf(" refuted");
        printf(" %.2f\n", (double)(clock() - t0) / CLOCKS_PER_SEC);
        fflush(stdout);
    }
    return 0;
}
