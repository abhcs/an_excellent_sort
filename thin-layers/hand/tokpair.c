/* tokpair.c -- per-comparator window contributions.  For each prefix (3 layers) and each
 * non-redundant layer 4: the window incidences w(c) = |[lo(c), hi(c)] cap W| after layer 4, and for
 * every non-redundant comparator (u, v) of a possible layer 5, the incidences of its two outputs.
 * Prints histograms: (a) contribution of one comparator of layer 4 (from the prefix); (b) of one
 * comparator of layer 5 (from each layer 4); (c) w of single channels after layer 4.
 * input as tokcore.c; usage: tokpair WLO WHI  (window ranks WLO..WHI) */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 12
typedef uint64_t word;
static int n, NW, WLO, WHI;
static uint32_t FULL;
typedef struct { int m; int a[MAXN / 2], b[MAXN / 2]; } Layer;
static void apply(const word *X, word *Y, const Layer *L) {
    memset(Y, 0, NW * sizeof(word));
    for (uint32_t s = 0; s < (1u << n); s++) {
        if (!(X[s >> 6] >> (s & 63) & 1)) continue;
        uint32_t t = s;
        for (int c = 0; c < L->m; c++) { int i = L->a[c], j = L->b[c];
            if ((t >> i & 1) && !(t >> j & 1)) t ^= (1u << i) | (1u << j); }
        Y[t >> 6] |= 1ull << (t & 63);
    }
}
/* exact intervals of a channel and of min/max of a pair, from weight statistics of X */
static int minw1[MAXN], maxw0[MAXN];               /* least weight with 1 on c; greatest weight with 0 on c */
static int minw11[MAXN][MAXN], maxw00[MAXN][MAXN]; /* least weight with 1 on both; greatest with 0 on both */
static int minw1any[MAXN][MAXN], maxw0any[MAXN][MAXN]; /* least weight with 1 on i or j; greatest with 0 on i or j */
static void stats(const word *X) {
    for (int i = 0; i < n; i++) { minw1[i] = 99; maxw0[i] = -1;
        for (int j = 0; j < n; j++) { minw11[i][j] = 99; maxw00[i][j] = -1; minw1any[i][j] = 99; maxw0any[i][j] = -1; } }
    for (uint32_t s = 0; s < (1u << n); s++) {
        if (!(X[s >> 6] >> (s & 63) & 1)) continue;
        int w = __builtin_popcount(s);
        for (int i = 0; i < n; i++) {
            int bi = s >> i & 1;
            if (bi && w < minw1[i]) minw1[i] = w;
            if (!bi && w > maxw0[i]) maxw0[i] = w;
            for (int j = i + 1; j < n; j++) {
                int bj = s >> j & 1;
                if (bi && bj && w < minw11[i][j]) minw11[i][j] = w;
                if (!bi && !bj && w > maxw00[i][j]) maxw00[i][j] = w;
                if ((bi || bj) && w < minw1any[i][j]) minw1any[i][j] = w;
                if ((!bi || !bj) && w > maxw0any[i][j]) maxw0any[i][j] = w;
            }
        }
    }
}
/* rank interval of a function f: lo = n-1-(greatest weight with f = 0), hi = n - (least weight with f = 1) */
static int winc(int lo, int hi) { int a = lo > WLO ? lo : WLO, b = hi < WHI ? hi : WHI; return b >= a ? b - a + 1 : 0; }
static int w_chan(int c) { return winc(n - 1 - maxw0[c], n - minw1[c]); }
static int w_min(int i, int j) { /* min(f_i,f_j): 1 iff both 1; 0 iff i or j is 0 */
    return winc(n - 1 - maxw0any[i][j], n - minw11[i][j]); }
static int w_max(int i, int j) { /* max: 1 iff i or j is 1; 0 iff both 0 */
    return winc(n - 1 - maxw00[i][j], n - minw1any[i][j]); }
static long long h4[8], h5[8], hc[4];
static int nonred(const word *X, int i, int j) {
    for (uint32_t s = 0; s < (1u << n); s++) if ((X[s >> 6] >> (s & 63) & 1) && (s >> i & 1) && !(s >> j & 1)) return 1;
    return 0;
}
static Layer *ALL; static int NALL;
static void gen(Layer *cur, uint32_t used, int c) {
    while (c < n && (used >> c & 1)) c++;
    if (c >= n) { ALL[NALL++] = *cur; return; }
    gen(cur, used | 1u << c, c + 1);
    for (int j = c + 1; j < n; j++) if (!(used >> j & 1)) { cur->a[cur->m] = c; cur->b[cur->m] = j; cur->m++; gen(cur, used | 1u << c | 1u << j, c + 1); cur->m--; }
}
int main(int argc, char **argv) {
    WLO = atoi(argv[1]); WHI = atoi(argv[2]);
    int D, P;
    if (scanf("%d %d %d", &n, &D, &P) != 3) return 1;
    NW = (1 << n) / 64; if (NW < 1) NW = 1; FULL = (1u << n) - 1;
    ALL = malloc(sizeof(Layer) * 40000); Layer cur; cur.m = 0; gen(&cur, 0, 0);
    static word X[64], Y[64];
    for (int idx = 0; idx < P; idx++) {
        int p; if (scanf("%d", &p) != 1) return 1;
        memset(X, 0, sizeof X);
        for (uint32_t s = 0; s < (1u << n); s++) X[s >> 6] |= 1ull << (s & 63);
        for (int l = 0; l < p; l++) { Layer L; if (scanf("%d", &L.m) != 1) return 1;
            for (int c = 0; c < L.m; c++) if (scanf("%d %d", &L.a[c], &L.b[c]) != 2) return 1;
            apply(X, Y, &L); memcpy(X, Y, sizeof X); }
        stats(X);
        for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (nonred(X, i, j)) h4[w_min(i, j) + w_max(i, j)]++;
        for (int ai = 0; ai < NALL; ai++) {
            int ok = 1;
            for (int c = 0; c < ALL[ai].m && ok; c++) ok = nonred(X, ALL[ai].a[c], ALL[ai].b[c]);
            if (!ok) continue;
            apply(X, Y, &ALL[ai]);
            stats(Y);
            for (int c = 0; c < n; c++) hc[w_chan(c)]++;
            for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (nonred(Y, i, j)) h5[w_min(i, j) + w_max(i, j)]++;
            stats(X);
        }
    }
    printf("one comparator of layer 4 (pairs after the prefix), outputs' incidences:"); for (int v = 0; v < 8; v++) printf(" %d:%lld", v, h4[v]); printf("\n");
    printf("one comparator of layer 5 (pairs after each layer 4), outputs' incidences:"); for (int v = 0; v < 8; v++) printf(" %d:%lld", v, h5[v]); printf("\n");
    printf("single channels after layer 4, incidences:"); for (int v = 0; v < 4; v++) printf(" %d:%lld", v, hc[v]); printf("\n");
    return 0;
}
