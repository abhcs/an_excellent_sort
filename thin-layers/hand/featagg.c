/* featagg.c -- data for a uniform cover formula.  For every prefix and non-redundant layer 4, each channel
 * gets a feature id (MODE 0: its interval after layer 4; MODE 1: interval and role in layer 4: min end,
 * max end, idle).  Aggregates (a) Wmax[f][g] = largest joint separation weight seen between channels
 * with features f, g; (b) every distinct (sorted feature multiset, S4) with its multiplicity.
 * Window {3,4,5}, n = 9.  output: "W f g w" lines, then "M S4 f1 ... f9" lines.  usage: featagg MODE */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 12
typedef uint64_t word;
static int n, NW, MODE;
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
static uint32_t T[MAXN], both1[MAXN + 1][MAXN], both0[MAXN + 1][MAXN], nonred[MAXN];
static int lo[MAXN], hi[MAXN];
static void stats(const word *X) {
    memset(T, 0, sizeof T); memset(both1, 0, sizeof both1); memset(both0, 0, sizeof both0); memset(nonred, 0, sizeof nonred);
    for (int c = 0; c < n; c++) { lo[c] = n; hi[c] = -1; }
    uint32_t full = (1u << n) - 1;
    for (uint32_t s = 0; s < (1u << n); s++) {
        if (!(X[s >> 6] >> (s & 63) & 1)) continue;
        int w = __builtin_popcount(s); uint32_t z = ~s & full;
        for (uint32_t o = s; o; o &= o - 1) { both1[w][__builtin_ctz(o)] |= s; nonred[__builtin_ctz(o)] |= z; }
        for (uint32_t o = z; o; o &= o - 1) both0[w][__builtin_ctz(o)] |= z;
        int k = n - 1 - w;
        for (uint32_t o = z; o; o &= o - 1) { int j = __builtin_ctz(o); uint32_t s2 = s | 1u << j;
            if (X[s2 >> 6] >> (s2 & 63) & 1) { T[k] |= 1u << j; if (k < lo[j]) lo[j] = k; if (k > hi[j]) hi[j] = k; } }
    }
}
static int sep(int k, int i, int j) { return !(both1[n - k][i] >> j & 1) || !(both0[n - 1 - k][i] >> j & 1); }
static int Wk[3] = {3, 4, 5};
static int Wmax[512][512];
/* hash set of multisets */
#define HS (1 << 22)
static uint64_t *hkey; static int *hcnt; static unsigned char (*hval)[10];
static void add_multiset(int *f, int S4) {
    int s[9]; memcpy(s, f, sizeof s);
    for (int i = 1; i < 9; i++) for (int j = i; j > 0 && s[j - 1] > s[j]; j--) { int t = s[j]; s[j] = s[j - 1]; s[j - 1] = t; }
    uint64_t h = 1469598103934665603ull ^ (uint64_t)S4;
    for (int i = 0; i < 9; i++) { h ^= (uint64_t)s[i] + 0x9e3779b97f4a7c15ull; h *= 1099511628211ull; h ^= h >> 31; }
    if (h == 0) h = 1;
    uint32_t pos = (uint32_t)(h & (HS - 1));
    while (hkey[pos] && hkey[pos] != h) pos = (pos + 1) & (HS - 1);
    if (!hkey[pos]) { hkey[pos] = h; hval[pos][0] = (unsigned char)S4; for (int i = 0; i < 9; i++) hval[pos][1 + i] = (unsigned char)s[i]; }
    hcnt[pos]++;
}
static Layer *ALL; static int NALL;
static void gen(Layer *cur, uint32_t used, int c) {
    while (c < n && (used >> c & 1)) c++;
    if (c >= n) { ALL[NALL++] = *cur; return; }
    gen(cur, used | 1u << c, c + 1);
    for (int j = c + 1; j < n; j++) if (!(used >> j & 1)) { cur->a[cur->m] = c; cur->b[cur->m] = j; cur->m++; gen(cur, used | 1u << c | 1u << j, c + 1); cur->m--; }
}
int main(int argc, char **argv) {
    MODE = atoi(argv[1]);
    int D, P;
    if (scanf("%d %d %d", &n, &D, &P) != 3) return 1;
    NW = (1 << n) / 64; if (NW < 1) NW = 1;
    ALL = malloc(sizeof(Layer) * 40000); Layer cur; cur.m = 0; gen(&cur, 0, 0);
    hkey = calloc(HS, sizeof(uint64_t)); hcnt = calloc(HS, sizeof(int)); hval = calloc(HS, 10);
    memset(Wmax, -1, sizeof Wmax);
    static word X[64], Y[64];
    for (int idx = 0; idx < P; idx++) {
        int p; if (scanf("%d", &p) != 1) return 1;
        memset(X, 0, sizeof X);
        for (uint32_t s = 0; s < (1u << n); s++) X[s >> 6] |= 1ull << (s & 63);
        for (int l = 0; l < p; l++) { Layer L; if (scanf("%d", &L.m) != 1) return 1;
            for (int c = 0; c < L.m; c++) if (scanf("%d %d", &L.a[c], &L.b[c]) != 2) return 1;
            apply(X, Y, &L); memcpy(X, Y, sizeof X); }
        stats(X);
        uint32_t nr0[MAXN]; memcpy(nr0, nonred, sizeof nr0);
        for (int ai = 0; ai < NALL; ai++) {
            int ok = 1;
            for (int c = 0; c < ALL[ai].m && ok; c++) ok = nr0[ALL[ai].a[c]] >> ALL[ai].b[c] & 1;
            if (!ok) continue;
            apply(X, Y, &ALL[ai]); stats(Y);
            int role[MAXN]; for (int c = 0; c < n; c++) role[c] = 2;
            for (int c = 0; c < ALL[ai].m; c++) { role[ALL[ai].a[c]] = 0; role[ALL[ai].b[c]] = 1; }
            int f[MAXN], S4 = 0;
            for (int c = 0; c < n; c++) {
                f[c] = lo[c] * 9 + hi[c];
                if (MODE == 1) f[c] = f[c] * 3 + role[c];
            }
            for (int q = 0; q < 3; q++) S4 += __builtin_popcount(T[Wk[q]]);
            for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) {
                int u = 0;
                for (int q = 0; q < 3; q++) { int k = Wk[q]; if ((T[k] >> i & 1) && (T[k] >> j & 1) && sep(k, i, j)) u++; }
                if (u > Wmax[f[i]][f[j]]) Wmax[f[i]][f[j]] = Wmax[f[j]][f[i]] = u;
            }
            add_multiset(f, S4);
        }
    }
    for (int a = 0; a < 512; a++) for (int b = a; b < 512; b++) if (Wmax[a][b] >= 0) printf("W %d %d %d\n", a, b, Wmax[a][b]);
    for (uint32_t pos = 0; pos < HS; pos++) if (hkey[pos]) {
        printf("M %d %d", hcnt[pos], hval[pos][0]);
        for (int i = 0; i < 9; i++) printf(" %d", hval[pos][1 + i]);
        printf("\n");
    }
    return 0;
}
