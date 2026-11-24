/* tophalf.c -- the one-sided window lemma.  For n = 9: R+_j = number of channels that can hold one of
 * the j largest elements (= channels that are 1 in some reachable state of weight j).  Window sum
 * S = sum_{j=4..6} (R+_j + R-_j) - 27.  For each prefix: least value over layers 4, 5 of
 * R+_4 + R+_5 + R+_6 (top half; bottom half by complement).  Prints per prefix the least top half and
 * least bottom half.  input as tokcore.c (prefix layers); exhaustive over non-redundant layers 4 and all
 * layers 5, pruned by monotonicity (reach only falls at separated pairs).  usage: tophalf */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 12
typedef uint64_t word;
static int n, NW;
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
/* U[w] = union of ones of weight-w states; Z[w] = union of zeros of weight-w states;
   both1[w] bitmatrix rows: both1[w][i] = channels j with some weight-w state having 1 on i and j */
static uint32_t U[MAXN + 1], Z[MAXN + 1], both1[MAXN + 1][MAXN], both0[MAXN + 1][MAXN], nonred[MAXN];
static void stats(const word *X) {
    memset(U, 0, sizeof U); memset(Z, 0, sizeof Z); memset(both1, 0, sizeof both1); memset(both0, 0, sizeof both0); memset(nonred, 0, sizeof nonred);
    uint32_t full = (1u << n) - 1;
    for (uint32_t s = 0; s < (1u << n); s++) {
        if (!(X[s >> 6] >> (s & 63) & 1)) continue;
        int w = __builtin_popcount(s); uint32_t z = ~s & full;
        U[w] |= s; Z[w] |= z;
        for (uint32_t o = s; o; o &= o - 1) { both1[w][__builtin_ctz(o)] |= s; nonred[__builtin_ctz(o)] |= z; }
        for (uint32_t o = z; o; o &= o - 1) both0[w][__builtin_ctz(o)] |= z;
    }
}
static int top(void) { return __builtin_popcount(U[4]) + __builtin_popcount(U[5]) + __builtin_popcount(U[6]); }
static int bot(void) { return __builtin_popcount(Z[5]) + __builtin_popcount(Z[4]) + __builtin_popcount(Z[3]); }
/* after one more layer, top-half reach = current - #comparators (i,j) inside U[w] never both 1 at weight w */
static Layer *ALL; static int NALL;
static void gen(Layer *cur, uint32_t used, int c) {
    while (c < n && (used >> c & 1)) c++;
    if (c >= n) { ALL[NALL++] = *cur; return; }
    gen(cur, used | 1u << c, c + 1);
    for (int j = c + 1; j < n; j++) if (!(used >> j & 1)) { cur->a[cur->m] = c; cur->b[cur->m] = j; cur->m++; gen(cur, used | 1u << c | 1u << j, c + 1); cur->m--; }
}
static int drop_top(const Layer *L) {   /* reach lost in the top half by layer L, from current stats */
    int d = 0;
    for (int c = 0; c < L->m; c++) { int i = L->a[c], j = L->b[c];
        for (int w = 4; w <= 6; w++) if ((U[w] >> i & 1) && (U[w] >> j & 1) && !(both1[w][i] >> j & 1)) d++; }
    return d;
}
static int drop_bot(const Layer *L) {
    int d = 0;
    for (int c = 0; c < L->m; c++) { int i = L->a[c], j = L->b[c];
        for (int w = 3; w <= 5; w++) if ((Z[w] >> i & 1) && (Z[w] >> j & 1) && !(both0[w][i] >> j & 1)) d++; }
    return d;
}
int main(void) {
    int D, P;
    if (scanf("%d %d %d", &n, &D, &P) != 3) return 1;
    NW = (1 << n) / 64; if (NW < 1) NW = 1;
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
        int t3 = top(), b3 = bot();
        uint32_t nr0[MAXN]; memcpy(nr0, nonred, sizeof nr0);   /* the prefix's non-redundant pairs */
        int besttop = 99, bestbot = 99, bestsum = 99;
        for (int ai = 0; ai < NALL; ai++) {
            int ok = 1;
            for (int c = 0; c < ALL[ai].m && ok; c++) ok = nr0[ALL[ai].a[c]] >> ALL[ai].b[c] & 1;
            if (!ok) continue;
            stats(X);
            int t4 = top() - drop_top(&ALL[ai]), b4 = bot() - drop_bot(&ALL[ai]);
            apply(X, Y, &ALL[ai]);
            stats(Y);
            /* sanity: recount reach after layer 4 directly */
            if (top() != t4 || bot() != b4) { fprintf(stderr, "reach mismatch\n"); return 2; }
            int mt = 99, mb = 99, ms = 99;
            for (int bi = 0; bi < NALL; bi++) {
                int dt = drop_top(&ALL[bi]), db = drop_bot(&ALL[bi]);
                if (t4 - dt < mt) mt = t4 - dt;
                if (b4 - db < mb) mb = b4 - db;
                if (t4 + b4 - dt - db < ms) ms = t4 + b4 - dt - db;
            }
            if (mt < besttop) besttop = mt;
            if (mb < bestbot) bestbot = mb;
            if (ms < bestsum) bestsum = ms;
        }
        printf("%d %d %d %d %d %d\n", idx, t3, b3, besttop, bestbot, bestsum);
        fflush(stdout);
    }
    return 0;
}
