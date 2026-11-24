/* tokfull.c -- unpruned cross-check of tokcore.c: for each prefix, every non-redundant layer A
 * (layer p+1) and EVERY layer B (layer p+2, all matchings, redundant comparators allowed); computes the
 * reachable set after B and its token sets directly (no images, no partial bounds), and prints the
 * least value over (A, B) of max_k |T(k)|.  A prefix is refuted by the cone bound at layer p+2 = D-2
 * when this is >= 5.  input as tokcore.c; output per prefix: idx #A #pairs least_max */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 12
typedef uint64_t word;
static int n, NW;
static uint32_t FULL;
typedef struct { int m; int a[MAXN / 2], b[MAXN / 2]; } Layer;
static Layer *ALL; static int NALL;
static void gen(Layer *cur, uint32_t used, int c) {
    while (c < n && (used >> c & 1)) c++;
    if (c >= n) { ALL[NALL++] = *cur; return; }
    gen(cur, used | 1u << c, c + 1);
    for (int j = c + 1; j < n; j++) if (!(used >> j & 1)) {
        cur->a[cur->m] = c; cur->b[cur->m] = j; cur->m++;
        gen(cur, used | 1u << c | 1u << j, c + 1);
        cur->m--; }
}
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
static int maxtok(const word *X) {
    uint32_t T[MAXN] = {0};
    for (uint32_t s = 0; s < (1u << n); s++) {
        if (!(X[s >> 6] >> (s & 63) & 1)) continue;
        int k = n - 1 - __builtin_popcount(s);
        for (int j = 0; j < n; j++) {
            if (s >> j & 1) continue;
            uint32_t s2 = s | 1u << j;
            if (X[s2 >> 6] >> (s2 & 63) & 1) T[k] |= 1u << j;
        }
    }
    int m = 0;
    for (int k = 0; k < n; k++) if (__builtin_popcount(T[k]) > m) m = __builtin_popcount(T[k]);
    return m;
}
static int nonredundant(const word *X, const Layer *L) {
    for (int c = 0; c < L->m; c++) {
        int i = L->a[c], j = L->b[c], ok = 0;
        for (uint32_t s = 0; s < (1u << n) && !ok; s++)
            if ((X[s >> 6] >> (s & 63) & 1) && (s >> i & 1) && !(s >> j & 1)) ok = 1;
        if (!ok) return 0;
    }
    return 1;
}
int main(void) {
    int D, P;
    if (scanf("%d %d %d", &n, &D, &P) != 3) return 1;
    NW = (1 << n) / 64; if (NW < 1) NW = 1; FULL = (1u << n) - 1;
    ALL = malloc(sizeof(Layer) * 40000); Layer cur; cur.m = 0; gen(&cur, 0, 0);
    static word X[64], Y[64], Z[64];
    for (int idx = 0; idx < P; idx++) {
        int p; if (scanf("%d", &p) != 1) return 1;
        memset(X, 0, sizeof X);
        for (uint32_t s = 0; s < (1u << n); s++) X[s >> 6] |= 1ull << (s & 63);
        for (int l = 0; l < p; l++) { Layer L; if (scanf("%d", &L.m) != 1) return 1;
            for (int c = 0; c < L.m; c++) if (scanf("%d %d", &L.a[c], &L.b[c]) != 2) return 1;
            apply(X, Y, &L); memcpy(X, Y, sizeof X); }
        long long nA = 0, npairs = 0; int least = 99;
        for (int ai = 0; ai < NALL; ai++) {
            if (!nonredundant(X, &ALL[ai])) continue;
            nA++;
            apply(X, Y, &ALL[ai]);
            for (int bi = 0; bi < NALL; bi++) {
                apply(Y, Z, &ALL[bi]);
                int m = maxtok(Z); npairs++;
                if (m < least) least = m;
            }
        }
        printf("%d %lld %lld %d\n", idx, nA, npairs, least); fflush(stdout);
    }
    return 0;
}
