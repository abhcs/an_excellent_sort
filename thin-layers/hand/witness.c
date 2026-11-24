/* witness.c -- the witness term calculus (efficient-prefixes.md section 7.4).
 * A term of a channel is a set of inputs whose 1s force the channel to 1; a clause a set whose 0s force
 * it to 0.  The channel's rank interval is [b-1, n-a], a = least term size, b = least clause size.
 * Through a comparator: min end = AND (terms: unions of a term of each side; clauses: both families),
 * max end = OR (terms: both families; clauses: unions).  With all minimal terms and clauses after the
 * prefix this is exact; with fewer witnesses every interval can only narrow, so window counts stay
 * lower bounds.  For each prefix and each non-redundant layer 4 the least window sum over layer 5 is
 * found by a DP over matchings (non-redundant comparators).
 * MODE (witnesses kept for each prefix channel): 0 all minimal; 1 minimum size only; 2 one of minimum
 * size; 3 sizes <= minimum + 1.  input as tokcore.c (n = 9, window {3,4,5}).  usage: witness MODE */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXN 12
#define MAXF 128
typedef uint64_t word;
static int n, NW, MODE;
typedef struct { int m; int a[MAXN / 2], b[MAXN / 2]; } Layer;
typedef struct { int k; uint16_t s[MAXF]; } Fam;
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
/* channel functions as truth tables: out[c][x] for input x */
static void tables(Layer *pre, int p, uint8_t out[MAXN][512]) {
    for (uint32_t x = 0; x < (1u << n); x++) {
        uint32_t t = x;
        for (int l = 0; l < p; l++) for (int c = 0; c < pre[l].m; c++) { int i = pre[l].a[c], j = pre[l].b[c];
            if ((t >> i & 1) && !(t >> j & 1)) t ^= (1u << i) | (1u << j); }
        for (int c = 0; c < n; c++) out[c][x] = t >> c & 1;
    }
}
static int pc(uint32_t s) { return __builtin_popcount(s); }
static void minimalize(Fam *f) {
    int k = 0; uint16_t o[MAXF];
    for (int i = 0; i < f->k; i++) {
        int dom = 0;
        for (int j = 0; j < f->k && !dom; j++) {
            if (j == i) continue;
            if ((f->s[j] & f->s[i]) == f->s[j] && (f->s[j] != f->s[i] || j < i)) dom = 1;
        }
        if (!dom) o[k++] = f->s[i];
    }
    memcpy(f->s, o, k * sizeof(uint16_t)); f->k = k;
}
static void restrict_mode(Fam *f) {
    int mn = 99; for (int i = 0; i < f->k; i++) if (pc(f->s[i]) < mn) mn = pc(f->s[i]);
    int k = 0;
    for (int i = 0; i < f->k; i++) {
        int sz = pc(f->s[i]);
        if (MODE == 1 && sz != mn) continue;
        if (MODE == 2 && (sz != mn || k >= 1)) continue;
        if (MODE == 3 && sz > mn + 1) continue;
        f->s[k++] = f->s[i];
    }
    f->k = k;
}
static void terms_of(uint8_t *tt, Fam *f, int clauses) {
    f->k = 0;
    for (uint32_t x = 0; x < (1u << n); x++) {
        uint32_t S = clauses ? (~x & ((1u << n) - 1)) : x;   /* clause: zero set of a false point */
        int val = tt[x];
        if (clauses ? val : !val) continue;
        /* minimal: no single-element change keeps the property */
        int minimal = 1;
        for (int i = 0; i < n && minimal; i++) if (S >> i & 1) {
            uint32_t y = clauses ? (x | 1u << i) : (x & ~(1u << i));
            if (clauses ? !tt[y] : tt[y]) minimal = 0;
        }
        if (minimal && f->k < MAXF) f->s[f->k++] = (uint16_t)S;
    }
}
static void fam_and(const Fam *a, const Fam *b, Fam *o) {   /* unions */
    o->k = 0;
    for (int i = 0; i < a->k; i++) for (int j = 0; j < b->k; j++) {
        uint16_t u = a->s[i] | b->s[j]; int dup = 0;
        for (int t = 0; t < o->k && !dup; t++) if (o->s[t] == u) dup = 1;
        if (!dup && o->k < MAXF) o->s[o->k++] = u;
    }
    minimalize(o);
}
static void fam_or(const Fam *a, const Fam *b, Fam *o) {
    o->k = 0;
    for (int i = 0; i < a->k && o->k < MAXF; i++) o->s[o->k++] = a->s[i];
    for (int j = 0; j < b->k && o->k < MAXF; j++) o->s[o->k++] = b->s[j];
    minimalize(o);
}
static int minsize(const Fam *f) { int m = 99; for (int i = 0; i < f->k; i++) if (pc(f->s[i]) < m) m = pc(f->s[i]); return m; }
static int min_union(const Fam *a, const Fam *b) { int m = 99; for (int i = 0; i < a->k; i++) for (int j = 0; j < b->k; j++) { int u = pc(a->s[i] | b->s[j]); if (u < m) m = u; } return m; }
static int winc(int lo, int hi) { int x = lo > 3 ? lo : 3, y = hi < 5 ? hi : 5; return y >= x ? y - x + 1 : 0; }
static int wab(int a, int b) { return winc(b - 1, n - a); }
static Layer *ALL; static int NALL;
static void gen(Layer *cur, uint32_t used, int c) {
    while (c < n && (used >> c & 1)) c++;
    if (c >= n) { ALL[NALL++] = *cur; return; }
    gen(cur, used | 1u << c, c + 1);
    for (int j = c + 1; j < n; j++) if (!(used >> j & 1)) { cur->a[cur->m] = c; cur->b[cur->m] = j; cur->m++; gen(cur, used | 1u << c | 1u << j, c + 1); cur->m--; }
}
static uint32_t nonredX(const word *X, int i) { uint32_t r = 0, full = (1u << n) - 1;
    for (uint32_t s = 0; s < (1u << n); s++) if ((X[s >> 6] >> (s & 63) & 1) && (s >> i & 1)) r |= ~s & full; return r; }
static int pairc[MAXN][MAXN], idlec[MAXN]; static uint32_t nr4[MAXN]; static int memo[1 << MAXN];
static int dp(uint32_t mask) {
    if (!mask) return 0;
    if (memo[mask] >= 0) return memo[mask];
    int i = __builtin_ctz(mask); uint32_t rest = mask & ~(1u << i);
    int best = idlec[i] + dp(rest);
    for (uint32_t r = rest; r; r &= r - 1) { int j = __builtin_ctz(r);
        if (!(nr4[i] >> j & 1)) continue;
        int v = pairc[i][j] + dp(rest & ~(1u << j)); if (v < best) best = v; }
    return memo[mask] = best;
}
int main(int argc, char **argv) {
    MODE = atoi(argv[1]);
    int D, P;
    if (scanf("%d %d %d", &n, &D, &P) != 3) return 1;
    NW = (1 << n) / 64; if (NW < 1) NW = 1;
    ALL = malloc(sizeof(Layer) * 40000); Layer cur; cur.m = 0; gen(&cur, 0, 0);
    static word X[64], Y[64];
    static uint8_t tt[MAXN][512];
    long long hist[40] = {0}; int fammax = 0;
    for (int idx = 0; idx < P; idx++) {
        int p; if (scanf("%d", &p) != 1) return 1;
        Layer pre[8];
        memset(X, 0, sizeof X);
        for (uint32_t s = 0; s < (1u << n); s++) X[s >> 6] |= 1ull << (s & 63);
        for (int l = 0; l < p; l++) { if (scanf("%d", &pre[l].m) != 1) return 1;
            for (int c = 0; c < pre[l].m; c++) if (scanf("%d %d", &pre[l].a[c], &pre[l].b[c]) != 2) return 1;
            apply(X, Y, &pre[l]); memcpy(X, Y, sizeof X); }
        tables(pre, p, tt);
        Fam T3[MAXN], C3[MAXN];
        for (int c = 0; c < n; c++) {
            terms_of(tt[c], &T3[c], 0); terms_of(tt[c], &C3[c], 1);
            if (T3[c].k > fammax) fammax = T3[c].k; if (C3[c].k > fammax) fammax = C3[c].k;
            restrict_mode(&T3[c]); restrict_mode(&C3[c]);
        }
        uint32_t nr3[MAXN]; for (int i = 0; i < n; i++) nr3[i] = nonredX(X, i);
        int best = 99;
        for (int ai = 0; ai < NALL; ai++) {
            const Layer *L = &ALL[ai]; int ok = 1;
            for (int c = 0; c < L->m && ok; c++) ok = nr3[L->a[c]] >> L->b[c] & 1;
            if (!ok) continue;
            Fam T4[MAXN], C4[MAXN];
            for (int c = 0; c < n; c++) { T4[c] = T3[c]; C4[c] = C3[c]; }
            for (int c = 0; c < L->m; c++) { int i = L->a[c], j = L->b[c];
                fam_and(&T3[i], &T3[j], &T4[i]); fam_or(&C3[i], &C3[j], &C4[i]);   /* min end */
                fam_or(&T3[i], &T3[j], &T4[j]); fam_and(&C3[i], &C3[j], &C4[j]); } /* max end */
            apply(X, Y, L);
            for (int i = 0; i < n; i++) nr4[i] = nonredX(Y, i);
            int a4[MAXN], b4[MAXN];
            for (int c = 0; c < n; c++) { a4[c] = minsize(&T4[c]); b4[c] = minsize(&C4[c]); idlec[c] = wab(a4[c], b4[c]); }
            for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) {
                int amin = min_union(&T4[i], &T4[j]), bmin = b4[i] < b4[j] ? b4[i] : b4[j];
                int amax = a4[i] < a4[j] ? a4[i] : a4[j], bmax = min_union(&C4[i], &C4[j]);
                pairc[i][j] = wab(amin, bmin) + wab(amax, bmax);
            }
            for (int m = 0; m < (1 << n); m++) memo[m] = -1;
            int v = dp((1u << n) - 1);
            if (v < best) best = v;
        }
        hist[best]++;
        printf("%d %d\n", idx, best); fflush(stdout);
    }
    fprintf(stderr, "mode %d: least window sum after layer 5 per prefix:", MODE);
    for (int v = 0; v < 40; v++) if (hist[v]) fprintf(stderr, " %d:%lld", v, hist[v]);
    fprintf(stderr, "  (largest family of minimal terms or clauses after the prefix: %d)\n", fammax);
    return 0;
}
