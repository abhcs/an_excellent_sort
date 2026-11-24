/* indep13/cls.c -- independent class and residual check for the D(13) proof (efficient-prefixes.md 9.1).
 *
 * Written without code from classcount.c, resid.c or assemble13.py, and with no hashes for identity:
 * every identification is an explicit channel permutation (with or without complement), found by search
 * and then checked state by state.  Hashes only choose which candidates to try.
 *
 * Family T3(11,4): the first layer and the second-layer classes of results/l2classes_11_4.json (their
 * cover is checked by verify_cover.py), and every third layer of at most a comparators that each swap
 * some state reachable after layer 2.  Each prefix P has the reachable set S_P (image of all 0-1
 * inputs after layer 3).
 *  - Class: if S_P or its complement is a permutation of the set stored for an earlier class, P joins
 *    that class; otherwise P starts a new one and its set is stored.  Equal classes extend to a depth-8
 *    sorter together or fail together (subsumption both ways; complement = reflection).
 *  - Residual: for every sentinel (value v, input channel s) let e be the end of its track (the
 *    sentinel moves to the max end of each comparator it meets if v = 1, to the min end if v = 0).
 *    R = {P(x) with bit e deleted : x_s = v}; bit e is v on every such image (checked).  If P had a
 *    depth-8 completion, removing the sentinel's track would leave a 10-channel sorter of depth 8 whose
 *    first three layers reach a permutation of R.  So if R or its complement is a permutation of the
 *    reachable set of a 10-channel prefix with no depth-8 completion, P has none either.  No condition
 *    on the track is needed.
 *  - A class is settled when one of its prefixes has such a residual, or when its stored set (or its
 *    complement) is a permutation of the reachable set of an 11-channel prefix with no depth-8 completion.
 * The two lemma lists (prefixes refuted by tok.c) are inputs; everything else is recomputed here.
 *
 * usage: cls FAMILY.txt LEMMAS10.txt LEMMAS11.txt WITNESS.out [MEMBERS.out]
 *   FAMILY.txt: n a, then L1 as "m i j ...", then R and R second layers "m i j ..." (family.py)
 *   LEMMAS*.txt: prefixes in the tok.c input format (idx n D p layers)
 *   WITNESS.out: one line per class, how it is settled, with the permutation used
 *   MEMBERS.out (optional): one line per prefix: second-layer class, third layer, class, complement, permutation
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 11
#define NWMAX 32
typedef uint64_t u64;
typedef struct { int m; int a[8], b[8]; } Layer;

static int n = N, A;

/* ---------- sets of states (bitsets over 2^m states) ---------- */
static int nwords(int m) { return m >= 6 ? (1 << m) / 64 : 1; }
static void apply(const u64 *S, u64 *T, int m, const Layer *L) {
    int nw = nwords(m);
    memset(T, 0, nw * sizeof(u64));
    for (int w = 0; w < nw; w++) {
        u64 v = S[w];
        while (v) {
            uint32_t u = (uint32_t)(w * 64 + __builtin_ctzll(v));
            v &= v - 1;
            for (int c = 0; c < L->m; c++)
                if ((u >> L->a[c] & 1) && !(u >> L->b[c] & 1)) u ^= (1u << L->a[c]) | (1u << L->b[c]);
            T[u >> 6] |= 1ull << (u & 63);
        }
    }
}
static void complement(const u64 *S, u64 *T, int m) {
    int nw = nwords(m);
    uint32_t all = (1u << m) - 1;
    memset(T, 0, nw * sizeof(u64));
    for (int w = 0; w < nw; w++) {
        u64 v = S[w];
        while (v) {
            uint32_t u = (uint32_t)(w * 64 + __builtin_ctzll(v)) ^ all;
            v &= v - 1;
            T[u >> 6] |= 1ull << (u & 63);
        }
    }
}
static int has(const u64 *S, uint32_t u) { return (int)(S[u >> 6] >> (u & 63) & 1); }

/* ---------- invariants: per weight, per channel and per pair of channels ---------- */
typedef struct {
    int m, cnt, wd[N + 1];
    uint16_t sig[N][N + 1];        /* states of weight w with a 1 on c */
    uint8_t pc[N][N][N + 1];       /* states of weight w with 1s on c and d */
    uint64_t ch[N], key;
} Sig;

static uint64_t mix(uint64_t h, uint64_t x) {
    h ^= x + 0x9e3779b97f4a7c15ull + (h << 6) + (h >> 2);
    h ^= h >> 33; h *= 0xff51afd7ed558ccdull; h ^= h >> 33; h *= 0xc4ceb9fe1a85ec53ull; h ^= h >> 33;
    return h;
}
static int cmpu64(const void *x, const void *y) {
    uint64_t a = *(const uint64_t *)x, b = *(const uint64_t *)y;
    return a < b ? -1 : a > b;
}
static void sigof(const u64 *S, int m, Sig *g) {
    memset(g, 0, sizeof *g);
    g->m = m;
    int nw = nwords(m);
    for (int w = 0; w < nw; w++) {
        u64 v = S[w];
        while (v) {
            uint32_t u = (uint32_t)(w * 64 + __builtin_ctzll(v));
            v &= v - 1;
            int k = __builtin_popcount(u);
            g->cnt++; g->wd[k]++;
            for (uint32_t b = u; b; b &= b - 1) {
                int c = __builtin_ctz(b);
                g->sig[c][k]++;
                for (uint32_t b2 = b & (b - 1); b2; b2 &= b2 - 1) g->pc[c][__builtin_ctz(b2)][k]++;
            }
        }
    }
    for (int c = 0; c < m; c++)
        for (int d = c + 1; d < m; d++) memcpy(g->pc[d][c], g->pc[c][d], sizeof g->pc[c][d]);
    for (int c = 0; c < m; c++) {
        uint64_t h = 7, ph[N];
        for (int k = 0; k <= m; k++) h = mix(h, g->sig[c][k]);
        int np = 0;
        for (int d = 0; d < m; d++) {
            if (d == c) continue;
            uint64_t q = 11;
            for (int k = 0; k <= m; k++) q = mix(q, g->pc[c][d][k]);
            ph[np++] = q;
        }
        qsort(ph, np, sizeof ph[0], cmpu64);
        for (int i = 0; i < np; i++) h = mix(h, ph[i]);
        g->ch[c] = h;
    }
    uint64_t sc[N];
    memcpy(sc, g->ch, m * sizeof sc[0]);
    qsort(sc, m, sizeof sc[0], cmpu64);
    uint64_t h = mix(13, (uint64_t)g->cnt);
    for (int k = 0; k <= m; k++) h = mix(h, g->wd[k]);
    for (int c = 0; c < m; c++) h = mix(h, sc[c]);
    g->key = h;
}

/* ---------- isomorphism: a permutation pi with pi(X) = Y, checked on every state ---------- */
static const u64 *IX, *IY; static const Sig *GX, *GY;
static int iord[N], icand[N], iperm[N], im;
static long long iso_calls, iso_leaves;
static int verify_map(void) {
    iso_leaves++;
    int nw = nwords(im);
    for (int w = 0; w < nw; w++) {
        u64 v = IX[w];
        while (v) {
            uint32_t u = (uint32_t)(w * 64 + __builtin_ctzll(v)), t = 0;
            v &= v - 1;
            for (uint32_t b = u; b; b &= b - 1) t |= 1u << iperm[__builtin_ctz(b)];
            if (!has(IY, t)) return 0;
        }
    }
    return 1;   /* pi is injective and |X| = |Y|, so pi(X) = Y */
}
static int iso_rec(int i, uint32_t used) {
    if (i == im) return verify_map();
    int c = iord[i];
    for (uint32_t cand = icand[c] & ~used; cand; cand &= cand - 1) {
        int d = __builtin_ctz(cand), ok = 1;
        for (int j = 0; j < i && ok; j++) {
            int c2 = iord[j];
            if (memcmp(GX->pc[c][c2], GY->pc[d][iperm[c2]], im + 1)) ok = 0;
        }
        if (!ok) continue;
        iperm[c] = d;
        if (iso_rec(i + 1, used | 1u << d)) return 1;
    }
    return 0;
}
static int iso(const u64 *X, const Sig *gx, const u64 *Y, const Sig *gy, int *perm) {
    iso_calls++;
    if (gx->m != gy->m || gx->cnt != gy->cnt || memcmp(gx->wd, gy->wd, sizeof gx->wd)) return 0;
    int m = gx->m;
    for (int c = 0; c < m; c++) {
        icand[c] = 0;
        for (int d = 0; d < m; d++)
            if (!memcmp(gx->sig[c], gy->sig[d], sizeof gx->sig[c]) && gx->ch[c] == gy->ch[d]) icand[c] |= 1 << d;
        if (!icand[c]) return 0;
    }
    for (int c = 0; c < m; c++) iord[c] = c;
    for (int i = 0; i < m; i++)
        for (int j = i + 1; j < m; j++)
            if (__builtin_popcount(icand[iord[j]]) < __builtin_popcount(icand[iord[i]])) { int t = iord[i]; iord[i] = iord[j]; iord[j] = t; }
    IX = X; IY = Y; GX = gx; GY = gy; im = m;
    if (!iso_rec(0, 0)) return 0;
    memcpy(perm, iperm, m * sizeof(int));
    return 1;
}

/* ---------- hash tables of stored sets ---------- */
typedef struct {
    int m, nset, cap, *next, *head, hbits;
    u64 *sets; uint64_t *keys; Sig *sigs;   /* sigs cached if cache_sigs */
    int cache_sigs;
} Table;
static void tinit(Table *t, int m, int hbits, int cache) {
    memset(t, 0, sizeof *t);
    t->m = m; t->hbits = hbits; t->cache_sigs = cache;
    t->head = malloc(sizeof(int) << hbits);
    for (long i = 0; i < (1L << hbits); i++) t->head[i] = -1;
}
static int tadd(Table *t, const u64 *S, const Sig *g) {
    if (t->nset == t->cap) {
        t->cap = t->cap ? 2 * t->cap : 1024;
        t->sets = realloc(t->sets, (size_t)t->cap * NWMAX * sizeof(u64));
        t->keys = realloc(t->keys, (size_t)t->cap * sizeof(uint64_t));
        t->next = realloc(t->next, (size_t)t->cap * sizeof(int));
        if (t->cache_sigs) t->sigs = realloc(t->sigs, (size_t)t->cap * sizeof(Sig));
    }
    int i = t->nset++;
    memcpy(t->sets + (size_t)i * NWMAX, S, NWMAX * sizeof(u64));
    t->keys[i] = g->key;
    if (t->cache_sigs) t->sigs[i] = *g;
    int b = (int)(g->key & ((1u << t->hbits) - 1));
    t->next[i] = t->head[b]; t->head[b] = i;
    return i;
}
/* find a stored set Y with pi(X) = Y; returns its index or -1 */
static int tfind(Table *t, const u64 *X, const Sig *gx, int *perm) {
    int b = (int)(gx->key & ((1u << t->hbits) - 1));
    for (int i = t->head[b]; i >= 0; i = t->next[i]) {
        if (t->keys[i] != gx->key) continue;
        const u64 *Y = t->sets + (size_t)i * NWMAX;
        static Sig gy;
        const Sig *py = t->cache_sigs ? &t->sigs[i] : (sigof(Y, t->m, &gy), &gy);
        if (iso(X, gx, Y, py, perm)) return i;
    }
    return -1;
}

/* ---------- lemma prefixes ---------- */
static int read_lemmas(const char *path, int m, Table *t, int **ids) {
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); exit(1); }
    int idx, nn, D, p, cnt = 0, cap = 1024;
    *ids = malloc(cap * sizeof(int));
    while (fscanf(f, "%d %d %d %d", &idx, &nn, &D, &p) == 4) {
        if (nn != m || D != 8) { fprintf(stderr, "%s: lemma %d has n=%d D=%d\n", path, idx, nn, D); exit(1); }
        Layer Ls[8];
        for (int l = 0; l < p; l++) {
            if (fscanf(f, "%d", &Ls[l].m) != 1) exit(1);
            for (int c = 0; c < Ls[l].m; c++) if (fscanf(f, "%d %d", &Ls[l].a[c], &Ls[l].b[c]) != 2) exit(1);
        }
        u64 S[NWMAX], T[NWMAX];
        memset(S, 0, sizeof S);
        for (uint32_t x = 0; x < (1u << m); x++) S[x >> 6] |= 1ull << (x & 63);
        for (int l = 0; l < p; l++) { apply(S, T, m, &Ls[l]); memcpy(S, T, sizeof S); }
        Sig g; sigof(S, m, &g);
        tadd(t, S, &g);
        if (cnt == cap) { cap *= 2; *ids = realloc(*ids, cap * sizeof(int)); }
        (*ids)[cnt++] = idx;
    }
    fclose(f);
    return cnt;
}

/* ---------- the family ---------- */
static Layer L1, L2s[400], L3;
static int R2;
static u64 S1[NWMAX];

typedef struct { int settled; int how; long pid; int r, v, s, e, lemma, comp, perm[N]; Layer l3; } Witness;
static Table classes, lem10, lem11;
static int *lemid10, *lemid11;
static Witness *wit; static int wcap;
static long *crep; static int *crep_r; static Layer *crep_l3;
static long nprefix, nres, nres_dup;
static FILE *members;

/* T2[r][v][s]: image after layer 2 of the inputs with x_s = v (the sentinel's subcube) */
static u64 T2cur[2][N][NWMAX];
static int track_e[2][N];      /* end of the track after layers 1-2 */

static int track(int v, int pos, const Layer *L) {
    for (int c = 0; c < L->m; c++)
        if (L->a[c] == pos || L->b[c] == pos) return v ? L->b[c] : L->a[c];
    return pos;
}
/* a sentinel start is a duplicate if another start gives the same track from layer 1 on */
static int dup_start(int v, int s) {
    for (int c = 0; c < L1.m; c++) {
        if (v == 1 && s == L1.a[c]) return 1;   /* +inf on the min end moves to the max end: same as starting there */
        if (v == 0 && s == L1.b[c]) return 1;
    }
    return 0;
}

static void try_residuals(long pid, int r, int cl) {
    for (int v = 0; v < 2 && !wit[cl].settled; v++)
        for (int s = 0; s < n && !wit[cl].settled; s++) {
            if (dup_start(v, s)) continue;
            u64 T3[NWMAX];
            apply(T2cur[v][s], T3, n, &L3);
            int e = track(v, track_e[v][s], &L3);
            u64 Rs[NWMAX];
            memset(Rs, 0, sizeof Rs);
            uint32_t low = (1u << e) - 1;
            for (int w = 0; w < nwords(n); w++) {
                u64 x = T3[w];
                while (x) {
                    uint32_t u = (uint32_t)(w * 64 + __builtin_ctzll(x));
                    x &= x - 1;
                    if ((int)(u >> e & 1) != v) { fprintf(stderr, "track end %d does not hold %d\n", e, v); exit(3); }
                    uint32_t q = (u & low) | ((u >> (e + 1)) << e);
                    Rs[q >> 6] |= 1ull << (q & 63);
                }
            }
            nres++;
            for (int comp = 0; comp < 2; comp++) {
                u64 X[NWMAX];
                if (comp) complement(Rs, X, n - 1); else memcpy(X, Rs, sizeof X);
                Sig g; sigof(X, n - 1, &g);
                int perm[N];
                int li = tfind(&lem10, X, &g, perm);
                if (li >= 0) {
                    Witness *W = &wit[cl];
                    W->settled = 1; W->how = 1; W->pid = pid; W->r = r; W->v = v; W->s = s; W->e = e;
                    W->lemma = lemid10[li]; W->comp = comp; memcpy(W->perm, perm, sizeof perm); W->l3 = L3;
                    break;
                }
            }
        }
}

static void one_prefix(int r, const u64 *S2) {
    u64 S3[NWMAX];
    apply(S2, S3, n, &L3);
    long pid = nprefix++;
    int cl = -1, comp = 0, perm[N];
    for (int cc = 0; cc < 2 && cl < 0; cc++) {
        u64 X[NWMAX];
        if (cc) complement(S3, X, n); else memcpy(X, S3, sizeof X);
        Sig g; sigof(X, n, &g);
        cl = tfind(&classes, X, &g, perm);
        comp = cc;
    }
    if (cl < 0) {
        Sig g; sigof(S3, n, &g);
        cl = tadd(&classes, S3, &g);
        comp = 0;
        for (int c = 0; c < n; c++) perm[c] = c;
        if (cl >= wcap) {
            wcap = wcap ? 2 * wcap : 1 << 16;
            wit = realloc(wit, wcap * sizeof(Witness));
            crep = realloc(crep, wcap * sizeof(long)); crep_r = realloc(crep_r, wcap * sizeof(int));
            crep_l3 = realloc(crep_l3, wcap * sizeof(Layer));
        }
        memset(&wit[cl], 0, sizeof wit[cl]);
        crep[cl] = pid; crep_r[cl] = r; crep_l3[cl] = L3;
    }
    if (members) {
        fprintf(members, "%d |", r);
        for (int c = 0; c < L3.m; c++) fprintf(members, " %d %d", L3.a[c], L3.b[c]);
        fprintf(members, " | %d %d", cl, comp);
        for (int c = 0; c < n; c++) fprintf(members, " %d", perm[c]);
        fprintf(members, "\n");
    }
    if (!wit[cl].settled) try_residuals(pid, r, cl);
}

/* third layers: the least free channel stays idle or takes a partner above it whose comparator swaps */
static uint32_t swaps2[N];
static void gen3(int r, const u64 *S2, uint32_t pool) {
    if (!pool) { one_prefix(r, S2); return; }
    int c = __builtin_ctz(pool);
    uint32_t rest = pool & ~(1u << c);
    gen3(r, S2, rest);
    if (L3.m == A) return;
    for (uint32_t cand = swaps2[c] & rest; cand; cand &= cand - 1) {
        int d = __builtin_ctz(cand);
        L3.a[L3.m] = c; L3.b[L3.m] = d; L3.m++;
        gen3(r, S2, rest & ~(1u << d));
        L3.m--;
    }
}

static void print_layer(FILE *f, const Layer *L) {
    fprintf(f, "[");
    for (int c = 0; c < L->m; c++) fprintf(f, "%s%d %d", c ? ", " : "", L->a[c], L->b[c]);
    fprintf(f, "]");
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: cls FAMILY LEMMAS10 LEMMAS11 WITNESS [MEMBERS]\n"); return 1; }
    FILE *f = fopen(argv[1], "r");
    if (!f || fscanf(f, "%d %d", &n, &A) != 2 || n > N || n < 7) { fprintf(stderr, "bad family\n"); return 1; }
    if (fscanf(f, "%d", &L1.m) != 1) return 1;
    for (int c = 0; c < L1.m; c++) if (fscanf(f, "%d %d", &L1.a[c], &L1.b[c]) != 2) return 1;
    if (fscanf(f, "%d", &R2) != 1 || R2 > 400) return 1;
    for (int r = 0; r < R2; r++) {
        if (fscanf(f, "%d", &L2s[r].m) != 1) return 1;
        for (int c = 0; c < L2s[r].m; c++) if (fscanf(f, "%d %d", &L2s[r].a[c], &L2s[r].b[c]) != 2) return 1;
    }
    fclose(f);
    tinit(&classes, n, 20, 0);
    tinit(&lem10, n - 1, 14, 1);
    tinit(&lem11, n, 10, 1);
    int nl10 = read_lemmas(argv[2], n - 1, &lem10, &lemid10);
    int nl11 = read_lemmas(argv[3], n, &lem11, &lemid11);
    fprintf(stderr, "lemmas: %d ten-channel, %d eleven-channel\n", nl10, nl11);
    if (argc > 5) members = fopen(argv[5], "w");
    u64 X0[NWMAX];
    memset(X0, 0, sizeof X0);
    for (uint32_t x = 0; x < (1u << n); x++) X0[x >> 6] |= 1ull << (x & 63);
    apply(X0, S1, n, &L1);
    long per_r[400];
    for (int r = 0; r < R2; r++) {
        u64 S2[NWMAX];
        apply(S1, S2, n, &L2s[r]);
        for (int c = 0; c < n; c++) {
            swaps2[c] = 0;
            for (int d = c + 1; d < n; d++) {
                int sw = 0;
                for (int w = 0; w < nwords(n) && !sw; w++) {
                    u64 x = S2[w];
                    while (x) {
                        uint32_t u = (uint32_t)(w * 64 + __builtin_ctzll(x));
                        x &= x - 1;
                        if ((u >> c & 1) && !(u >> d & 1)) { sw = 1; break; }
                    }
                }
                if (sw) swaps2[c] |= 1u << d;
            }
        }
        for (int v = 0; v < 2; v++)
            for (int s = 0; s < n; s++) {
                u64 Z[NWMAX], Y[NWMAX];
                memset(Z, 0, sizeof Z);
                for (uint32_t x = 0; x < (1u << n); x++) if ((int)(x >> s & 1) == v) Z[x >> 6] |= 1ull << (x & 63);
                apply(Z, Y, n, &L1);
                apply(Y, T2cur[v][s], n, &L2s[r]);
                track_e[v][s] = track(v, track(v, s, &L1), &L2s[r]);
            }
        long before = nprefix;
        L3.m = 0;
        gen3(r, S2, (1u << n) - 1);
        per_r[r] = nprefix - before;
        if (r % 20 == 0) fprintf(stderr, "second-layer class %d: %ld prefixes, %d classes so far\n", r, nprefix, classes.nset);
    }
    /* classes not settled by a residual: their stored set against the 11-channel lemmas */
    int byres = 0, bydir = 0, unset = 0;
    for (int cl = 0; cl < classes.nset; cl++) {
        if (wit[cl].settled) { byres++; continue; }
        const u64 *S = classes.sets + (size_t)cl * NWMAX;
        for (int comp = 0; comp < 2 && !wit[cl].settled; comp++) {
            u64 X[NWMAX];
            if (comp) complement(S, X, n); else memcpy(X, S, sizeof X);
            Sig g; sigof(X, n, &g);
            int perm[N], li = tfind(&lem11, X, &g, perm);
            if (li >= 0) {
                Witness *W = &wit[cl];
                W->settled = 1; W->how = 2; W->lemma = lemid11[li]; W->comp = comp; memcpy(W->perm, perm, sizeof perm);
            }
        }
        if (wit[cl].settled) bydir++; else unset++;
    }
    FILE *wf = fopen(argv[4], "w");
    fprintf(wf, "# class\trepresentative (second-layer class, third layer)\tsettled by\twitness\n");
    for (int cl = 0; cl < classes.nset; cl++) {
        Witness *W = &wit[cl];
        fprintf(wf, "%d\t%d ", cl, crep_r[cl]);
        print_layer(wf, &crep_l3[cl]);
        if (W->how == 1) {
            fprintf(wf, "\tresidual\tprefix %d ", W->r);
            print_layer(wf, &W->l3);
            fprintf(wf, " sentinel %s at input %d, track end %d; 10-channel lemma %d, complement %d, perm",
                    W->v ? "+inf" : "-inf", W->s, W->e, W->lemma, W->comp);
            for (int c = 0; c < n - 1; c++) fprintf(wf, " %d", W->perm[c]);
        } else if (W->how == 2) {
            fprintf(wf, "\tdirect\t11-channel lemma %d, complement %d, perm", W->lemma, W->comp);
            for (int c = 0; c < n; c++) fprintf(wf, " %d", W->perm[c]);
        } else fprintf(wf, "\tUNSETTLED\t-");
        fprintf(wf, "\n");
    }
    fclose(wf);
    if (members) fclose(members);
    printf("family: %d second-layer classes, %ld prefixes; first class %ld prefixes\n", R2, nprefix, per_r[0]);
    printf("classes (explicit permutations, with complement): %d\n", classes.nset);
    printf("residuals tried: %ld; isomorphism searches: %lld, leaves checked: %lld\n", nres, iso_calls, iso_leaves);
    printf("settled through a residual: %d; directly: %d; UNSETTLED: %d\n", byres, bydir, unset);
    return unset ? 4 : 0;
}
