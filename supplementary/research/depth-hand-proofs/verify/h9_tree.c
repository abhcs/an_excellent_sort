/* h9_tree.c -- (H9) without SAT: a case tree over layers 2..5 whose leaves carry small
 * certificates, finished by an exact search over the last two layers where no certificate applies.
 *
 * Setting (h9.md section 2): nine channels; L1 = (0,1)(2,3)(4,5), channels 6,7,8 idle; L2 runs over
 * one representative of each of the 69 classes of matchings with at most 3 comparators (relabellings
 * fixing L1, and reflection; relabel + untangle keeps every layer's size); L3, L4, L5, L6 run over
 * ALL 2620 matchings on 9 channels; L7 runs over the adjacent matchings (h9.md Lemma 6: after deleting the
 * last-layer comparators that never fire, only pairs (i,i+1) remain).
 *
 * Certificates, tried in this order at each node:
 *   B3  four infinities keep the five reals apart in layers 1-3  (D(5) >= 5)
 *   B4  four infinities; in layers 1-4 the reals meet in at most one layer, or in exactly two layers
 *       with one comparator each  (D(5) >= 5, or Lemma 3)
 *   C4  some output's target value, on the states after layer 4, depends on all 9 channels; three
 *       layers leave a channel depending on at most 8  (Tool D)
 *   B5  four infinities; in layers 1-5 the reals meet in at most two layers, or in exactly three of
 *       which the first two have one comparator each  (D(5) >= 5, or Lemma 3)
 *   B5s as B5 but using S(5) >= 9: the reals' network has at most 8 comparators (counted only if no
 *       B5 certificate exists; reported separately because the README does not prove S(5) >= 9)
 *   C5  some output's target value, on the states after layer 5, depends on at least 5 channels; two
 *       layers leave a channel depending on at most 4  (Tool D)
 *   E   exhaustive: no L6 and adjacent L7 sort the states after layer 5.
 *   H5  (-p) four consecutive nontrivial weight levels, two adjacent heavy
 *       levels: the rank-profile hand lemma excludes a two-layer ending.
 * A leaf where E finds a completion would be a sorting network refuting (H9); it is printed and
 * checked on all 512 inputs.
 * usage: h9_tree [-r] [-n] [-l] [-s] [-e] [m1 cap2]   (default 3 3, which is (H9).  Control: with m1 = 4, depth-7
 *        sorting networks exist, and the program must find some; it prints at most 5 and counts them.)
 *   -r  non-redundant normal form: layers 2..5 use only comparators that fire on some state reaching
 *       them (deleting a comparator that never fires changes nothing, so this loses no network)
 *   -l  list the (L2, L3) prefixes that B3 does not settle, as "L2 | L3"
 *   -n  do not use S(5) >= 9 (no B5s certificates; those leaves go on to C5 and E)
 *   -s  one summary line per class of L2: its prefixes and certificates at each layer
 *   -e  list the leaves settled by E, as "L2 | L3 | L4 | L5", with the fewest inputs any L6 + adjacent
 *       L7 leaves unsorted; with -p, also list the H5 leaves
 *   -p  use the rank-profile hand obstruction before any ending search */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <assert.h>
#define N 9
#define NM 2620
#define NW ((NM + 63) / 64)
typedef struct { int m; int a[4], b[4]; } match_t;
static match_t all[NM], cur; static int nall;
static void gen(int used, int start) {
    int first = -1;
    for (int i = start; i < N; i++) if (!(used >> i & 1)) { first = i; break; }
    if (first < 0) { all[nall++] = cur; return; }
    gen(used | 1 << first, first + 1);
    for (int j = first + 1; j < N; j++) if (!(used >> j & 1)) {
        cur.a[cur.m] = first; cur.b[cur.m] = j; cur.m++;
        gen(used | 1 << first | 1 << j, first + 1); cur.m--;
    }
}
/* ---------- classes of L2 ---------- */
static int m1 = 3, cap2 = 3, nonred = 0, listb3 = 0, nosize = 0, liste = 0, summary = 0, profiles = 0;
/* There are only 36 pairs. The old index 9*a+b reached 71 for (7,8),
 * which is an undefined shift in uint64_t and can alias another pair. */
static int pair_index(int a, int b) { return a * (2 * N - a - 1) / 2 + b - a - 1; }
static uint64_t pm[NM];                         /* one distinct bit per channel pair */
static uint64_t firing(const int *S, int ns) {  /* pairs (a,b), a<b, with a 1 on a and 0 on b in S */
    uint64_t f = 0;
    for (int q = 0; q < ns; q++)
        for (int a = 0; a < N; a++) if (S[q] >> a & 1)
            for (int b = a + 1; b < N; b++) if (!(S[q] >> b & 1)) f |= 1ULL << pair_index(a, b);
    return f;
}
static int heavy_profile(const int *S, int ns, int *start, int *heavy) {
    int counts[N + 1] = {0};
    for (int q = 0; q < ns; q++) counts[N - __builtin_popcount((unsigned)S[q])]++;
    for (int a = 1; a + 3 < N; a++) {
        if (counts[a] < 2 || counts[a+1] < 2 || counts[a+2] < 2 || counts[a+3] < 2) continue;
        for (int b = a; b < a + 3; b++) if (counts[b] >= 3 && counts[b+1] >= 3) {
            *start = a; *heavy = b; return 1;
        }
    }
    return 0;
}
#define ADMIT(j, f) (!nonred || !(pm[j] & ~(f)))
static int grp[480][N], ngrp;
static uint64_t code(const match_t *M, const int *p) {
    int part[N]; for (int c = 0; c < N; c++) part[c] = 15;
    for (int e = 0; e < M->m; e++) { int a = p[M->a[e]], b = p[M->b[e]]; part[a] = b; part[b] = a; }
    uint64_t x = 0; for (int c = 0; c < N; c++) x = x << 4 | part[c]; return x;
}
static int perms[120][5], nperm;                /* all permutations of {0..k-1} */
static void permgen(int k, int *p, int d) {
    if (d == k) { memcpy(perms[nperm++], p, sizeof(int) * 5); return; }
    for (int i = d; i < k; i++) {
        int t = p[d]; p[d] = p[i]; p[i] = t; permgen(k, p, d + 1); t = p[d]; p[d] = p[i]; p[i] = t;
    }
}
/* the relabellings that map L1 = (0,1)(2,3)..(2m1-2,2m1-1) to itself keeping each comparator's
 * orientation (permute the pairs, permute the idle channels), each also composed with reflection
 * c -> 8-c followed by a relabelling taking the reflected L1 back to L1 */
static void make_group(void) {
    int idle = N - 2 * m1, p[5], canon[N];
    for (int i = 0; i < m1; i++) { canon[7 - 2 * i] = 2 * i; canon[8 - 2 * i] = 2 * i + 1; }
    for (int i = 0; i < idle; i++) canon[i] = 2 * m1 + i;
    int pp[120][5], npp, ip[120][5], nip;
    nperm = 0; for (int i = 0; i < 5; i++) p[i] = i; permgen(m1, p, 0);
    npp = nperm; memcpy(pp, perms, sizeof pp);
    nperm = 0; for (int i = 0; i < 5; i++) p[i] = i; permgen(idle, p, 0);
    nip = nperm; memcpy(ip, perms, sizeof ip);
    for (int r = 0; r < 2; r++) for (int s = 0; s < npp; s++) for (int t = 0; t < nip; t++) {
        int pi[N];
        for (int i = 0; i < m1; i++) { pi[2 * i] = 2 * pp[s][i]; pi[2 * i + 1] = 2 * pp[s][i] + 1; }
        for (int i = 0; i < idle; i++) pi[2 * m1 + i] = 2 * m1 + ip[t][i];
        for (int c = 0; c < N; c++) grp[ngrp][c] = r ? pi[canon[8 - c]] : pi[c];
        ngrp++;
    }
}
static int is_rep(const match_t *M) {
    uint64_t me = code(M, grp[0]);
    for (int g = 1; g < ngrp; g++) if (code(M, grp[g]) < me) return 0;
    return 1;
}
/* ---------- four infinities ---------- */
/* k = number of layers so far in which two reals met, s = total number of such comparators,
 * f1 = count in the first such layer, ft = the first two such layers had one comparator each */
typedef struct { uint16_t pos, plus; uint8_t k, s, f1, ft; } cfg_t;
static int alive(const cfg_t *c) {           /* can this still end in a B3/B4/B5/B5s certificate? */
    return c->k <= 2 || (c->k == 3 && (c->ft || c->s <= 4)) || (c->k == 4 && c->s <= 4);
}
static int step(cfg_t *c, const match_t *M) {
    uint16_t pos = c->pos, plus = c->plus; int rr = 0;
    for (int e = 0; e < M->m; e++) {
        int a = M->a[e], b = M->b[e];
        int ia = pos >> a & 1, ib = pos >> b & 1;
        if (!ia && !ib) { rr++; continue; }
        int va = ia ? ((plus >> a & 1) ? 2 : 0) : 1, vb = ib ? ((plus >> b & 1) ? 2 : 0) : 1;
        if (va > vb) {
            uint16_t sa = plus >> a & 1, sb = plus >> b & 1;
            pos = (pos & ~(1 << a | 1 << b)) | (ib << a) | (ia << b);
            plus = (plus & ~(1 << a | 1 << b)) | (sb << a) | (sa << b);
        }
    }
    cfg_t d = *c; d.pos = pos; d.plus = plus;
    if (rr) {
        if (d.k == 0) d.f1 = (uint8_t)rr;
        if (d.k == 1) d.ft = (d.f1 == 1 && rr == 1);
        d.k++; d.s = (uint8_t)(d.s + rr > 15 ? 15 : d.s + rr);
    }
    if (!alive(&d)) return -1;
    *c = d; return 0;
}
static int cmpcfg(const void *x, const void *y) { return memcmp(x, y, sizeof(cfg_t)); }
static int advance(const cfg_t *in, int nin, cfg_t *out, const match_t *M) {
    int n = 0;
    for (int q = 0; q < nin; q++) { cfg_t c = in[q]; if (step(&c, M) == 0) out[n++] = c; }
    qsort(out, n, sizeof(cfg_t), cmpcfg);
    int u = 0;
    for (int q = 0; q < n; q++) if (u == 0 || memcmp(&out[q], &out[u - 1], sizeof(cfg_t))) out[u++] = out[q];
    return u;
}
/* ---------- states ---------- */
static int apply(int x, const match_t *M) {
    for (int e = 0; e < M->m; e++) {
        int a = M->a[e], b = M->b[e];
        if ((x >> a & 1) && !(x >> b & 1)) x ^= 1 << a | 1 << b;
    }
    return x;
}
static int image(const int *in, int nin, int *out, const match_t *M) {
    uint64_t seen[8] = {0}; int n = 0;
    for (int q = 0; q < nin; q++) {
        int y = apply(in[q], M);
        if (!(seen[y >> 6] >> (y & 63) & 1)) { seen[y >> 6] |= 1ULL << (y & 63); out[n++] = y; }
    }
    return n;
}
/* does the target value of some output channel depend on at least `need` channels on S? */
static int cone(const int *S, int ns, int need) {
    uint64_t in[8] = {0};
    for (int q = 0; q < ns; q++) in[S[q] >> 6] |= 1ULL << (S[q] & 63);
    int sens[N] = {0};
    for (int q = 0; q < ns; q++) for (int c = 0; c < N; c++) {
        int t = S[q] | 1 << c;
        if (!(S[q] >> c & 1) && (in[t >> 6] >> (t & 63) & 1)) sens[c] |= 1 << __builtin_popcount(S[q]);
    }
    for (int k = 0; k < N; k++) {
        int w = 8 - k, cnt = 0;
        for (int c = 0; c < N; c++) if (sens[c] >> w & 1) cnt++;
        if (cnt >= need) return 1;
    }
    return 0;
}
/* exact: is there a matching L6 and an adjacent L7 with L7 L6 (S) sorted? */
static int completes(const int *S, int ns, int *w6, int *w7) {
    for (int j = 0; j < nall; j++) {
        int used = 0, ok = 1;
        for (int q = 0; q < ns && ok; q++) {
            int y = apply(S[q], &all[j]), w = __builtin_popcount(y);
            int srt = ((1 << w) - 1) << (N - w);
            if (y == srt) continue;
            if (w == 0 || w == N) { ok = 0; break; }
            int i = 8 - w;                         /* the pair (i, i+1) straddles the 0/1 boundary */
            if (y != (srt ^ (1 << i) ^ (1 << (i + 1)))) { ok = 0; break; }
            used |= 1 << i;
        }
        if (ok && !(used & (used << 1))) { *w6 = j; *w7 = used; return 1; }
    }
    return 0;
}
/* the fewest states of S that some L6 + adjacent L7 fails to sort */
static int closest(const int *S, int ns) {
    int best = 1 << 30;
    for (int j = 0; j < nall; j++) {
        int bad = 0, used = 0, ok[1 << N];   /* greedy: count states not of the allowed forms */
        for (int q = 0; q < ns; q++) {
            int y = apply(S[q], &all[j]), w = __builtin_popcount(y), srt = ((1 << w) - 1) << (N - w);
            ok[q] = 1;
            if (y == srt) continue;
            int i = 8 - w;
            if (w == 0 || w == N || y != (srt ^ (1 << i) ^ (1 << (i + 1)))) { bad++; ok[q] = 0; continue; }
            used |= 1 << i;
        }
        if (used & (used << 1)) bad++;      /* two boundary swaps that cannot share a layer */
        if (bad < best) best = bad;
    }
    return best;
}
static void pr(const match_t *M) {
    if (!M->m) printf("-");
    for (int e = 0; e < M->m; e++) printf("(%d,%d)", M->a[e], M->b[e]);
}

static uint64_t BM[3][1 << N][NW];     /* BM[b][R]: matchings with at most b comparators inside R */
static int sorts9(const match_t *const *L, int d) {
    for (int x = 0; x < (1 << N); x++) {
        int y = x;
        for (int t = 0; t < d; t++) y = apply(y, L[t]);
        int w = __builtin_popcount(y);
        if (y != ((1 << w) - 1) << (N - w)) return 0;
    }
    return 1;
}
int main(int argc, char **argv) {
    uint64_t pair_bits = 0;
    for (int a = 0; a < N; a++) for (int b = a + 1; b < N; b++) {
        int bit = pair_index(a, b);
        assert(0 <= bit && bit < N * (N - 1) / 2 && bit < 64);
        assert(!(pair_bits & (1ULL << bit)));
        pair_bits |= 1ULL << bit;
    }
    assert(__builtin_popcountll(pair_bits) == N * (N - 1) / 2);
    int pos_args[2], npos = 0;
    for (int a = 1; a < argc; a++) {
        if (!strcmp(argv[a], "-r")) nonred = 1;
        else if (!strcmp(argv[a], "-l")) listb3 = 1;
        else if (!strcmp(argv[a], "-n")) nosize = 1;
        else if (!strcmp(argv[a], "-e")) liste = 1;
        else if (!strcmp(argv[a], "-s")) summary = 1;
        else if (!strcmp(argv[a], "-p")) profiles = 1;
        else if (npos < 2) pos_args[npos++] = atoi(argv[a]);
    }
    if (npos == 2) { m1 = pos_args[0]; cap2 = pos_args[1]; }
    if (m1 < 2 || m1 > 4 || cap2 < 0 || cap2 > 4) { fprintf(stderr, "need 2 <= m1 <= 4, cap2 <= 4\n"); return 2; }
    gen(0, 0); make_group();
    for (int j = 0; j < nall; j++)
        for (int e = 0; e < all[j].m; e++) pm[j] |= 1ULL << pair_index(all[j].a[e], all[j].b[e]);
    for (int R = 0; R < (1 << N); R++) if (__builtin_popcount(R) == 5)
        for (int j = 0; j < nall; j++) {
            int in = 0;
            for (int e = 0; e < all[j].m; e++) if ((R >> all[j].a[e] & 1) && (R >> all[j].b[e] & 1)) in++;
            for (int b = 0; b < 3; b++) if (in <= b) BM[b][R][j / 64] |= 1ULL << (j % 64);
        }
    match_t L1; L1.m = m1;
    for (int e = 0; e < m1; e++) { L1.a[e] = 2 * e; L1.b[e] = 2 * e + 1; }
    static cfg_t c0[4096], c1[4096], c2[4096], c3[4096], c4[4096];
    int n0 = 0;
    for (int pos = 0; pos < (1 << N); pos++) if (__builtin_popcount(pos) == 4)
        for (int sg = 0; sg < (1 << N); sg++) if ((sg & ~pos) == 0) {
            cfg_t c; memset(&c, 0, sizeof c); c.pos = (uint16_t)pos; c.plus = (uint16_t)sg; c0[n0++] = c;
        }
    int n1 = advance(c0, n0, c1, &L1);
    static int S0[1 << N], S1[1 << N], S2[1 << N], S3[1 << N], S4[1 << N], S5[1 << N];
    for (int x = 0; x < (1 << N); x++) S0[x] = x;
    int s1 = image(S0, 1 << N, S1, &L1);
    long reps = 0, t3 = 0, b3 = 0, t4 = 0, b4 = 0, k4 = 0, t5 = 0, b5 = 0, b5s = 0, k5 = 0, h5 = 0, ex = 0, found = 0;
    for (int i = 0; i < nall; i++) {
        if (all[i].m > cap2 || !is_rep(&all[i]) || !ADMIT(i, firing(S1, s1))) continue;
        reps++;
        long o3 = t3, ob3 = b3, o4 = t4, ok4c = k4, o5 = t5, ok5c = k5, oh5 = h5, oex = ex;
        int n2 = advance(c1, n1, c2, &all[i]), s2 = image(S1, s1, S2, &all[i]);
        uint64_t f2 = firing(S2, s2);
        for (int j = 0; j < nall; j++) {
            if (!ADMIT(j, f2)) continue;
            t3++;
            int n3 = advance(c2, n2, c3, &all[j]), blind = 0;
            for (int q = 0; q < n3; q++) if (c3[q].k == 0) blind = 1;
            if (blind) { b3++; continue; }
            if (listb3) { pr(&all[i]); printf(" | "); pr(&all[j]); printf("\n"); }
            uint64_t ok4[NW] = {0};
            for (int q = 0; q < n3; q++) {
                int R = ~c3[q].pos & 511, b;
                if (c3[q].k == 1) b = c3[q].f1 == 1 ? 1 : 0;
                else if (c3[q].k == 2 && c3[q].ft) b = 0;
                else continue;
                for (int w = 0; w < NW; w++) ok4[w] |= BM[b][R][w];
            }
            int s3 = image(S2, s2, S3, &all[j]);
            uint64_t f3 = firing(S3, s3);
            for (int k = 0; k < nall; k++) {
                if (!ADMIT(k, f3)) continue;
                t4++;
                if (ok4[k / 64] >> (k % 64) & 1) { b4++; continue; }
                int s4 = image(S3, s3, S4, &all[k]);
                if (cone(S4, s4, 9)) { k4++; continue; }
                int n4 = advance(c3, n3, c4, &all[k]);
                uint64_t ok5[NW] = {0}, ok5s[NW] = {0};
                for (int q = 0; q < n4; q++) {
                    const cfg_t *c = &c4[q]; int R = ~c->pos & 511, b = -1, bs = -1;
                    if (c->k <= 1) b = 2;                       /* any L5 (at most 2 inside 5 reals) */
                    else if (c->k == 2) { if (c->ft) b = 2; else { b = 0; bs = 4 - c->s; } }
                    else if (c->k == 3) { if (c->ft) b = 0; else if (c->s <= 4) bs = 0; }
                    else if (c->k == 4 && c->s <= 4) bs = 0;
                    if (b >= 0) for (int w = 0; w < NW; w++) ok5[w] |= BM[b][R][w];
                    if (bs >= 1 || (bs == 0 && b < 0)) for (int w = 0; w < NW; w++) ok5s[w] |= BM[bs > 2 ? 2 : bs][R][w];
                }
                uint64_t f4 = firing(S4, s4);
                for (int l = 0; l < nall; l++) {
                    if (!ADMIT(l, f4)) continue;
                    t5++;
                    if (ok5[l / 64] >> (l % 64) & 1) { b5++; continue; }
                    if (!nosize && (ok5s[l / 64] >> (l % 64) & 1)) { b5s++; continue; }
                    int s5 = image(S4, s4, S5, &all[l]);
                    if (cone(S5, s5, 5)) { k5++; continue; }
                    int start, heavy;
                    if (profiles && heavy_profile(S5, s5, &start, &heavy)) {
                        h5++;
                        if (liste) {
                            pr(&all[i]); printf(" | "); pr(&all[j]); printf(" | "); pr(&all[k]);
                            printf(" | "); pr(&all[l]);
                            printf("   (%d states; H5 cuts %d..%d; heavy %d,%d)\n", s5, start, start + 3, heavy, heavy + 1);
                        }
                        continue;
                    }
                    int w6, w7;
                    if (completes(S5, s5, &w6, &w7)) {
                        match_t L7; L7.m = 0;
                        for (int p = 0; p < 8; p++) if (w7 >> p & 1) { L7.a[L7.m] = p; L7.b[L7.m] = p + 1; L7.m++; }
                        const match_t *net[7] = { &L1, &all[i], &all[j], &all[k], &all[l], &all[w6], &L7 };
                        if (!sorts9(net, 7)) { printf("BUG: completion does not sort\n"); return 3; }
                        if (++found <= 5) {
                            printf("sorting network:");
                            for (int t = 0; t < 7; t++) { printf(" "); pr(net[t]); }
                            printf("\n");
                        }
                    } else {
                        ex++;
                        if (liste) {
                            pr(&all[i]); printf(" | "); pr(&all[j]); printf(" | "); pr(&all[k]);
                            printf(" | "); pr(&all[l]);
                            printf("   (%d states; best L6 leaves %d unsorted)\n", s5, closest(S5, s5));
                        }
                    }
                }
            }
        }
        if (summary) {
            pr(&all[i]);
            printf(" | L3 %ld, B3 fails %ld | L4 %ld, C4 %ld | L5 %ld, C5 %ld | H5 %ld | E %ld\n", t3 - o3,
                   (t3 - o3) - (b3 - ob3), t4 - o4, k4 - ok4c, t5 - o5, k5 - ok5c, h5 - oh5, ex - oex);
        }
    }
    printf("|L1| = %d, |L2| <= %d%s; classes of L2: %ld\n", m1, cap2,
           nonred ? ", only comparators that fire" : "", reps);
    printf("layer 3: %ld prefixes; B3 settles %ld\n", t3, b3);
    printf("layer 4: %ld prefixes; B4 settles %ld, C4 %ld\n", t4, b4, k4);
    printf("layer 5: %ld prefixes; B5 settles %ld, B5s (uses S(5)>=9) %ld, C5 %ld, H5 %ld, exhaustive %ld\n",
           t5, b5, b5s, k5, h5, ex);
    printf("leaves where a depth-7 sorting network exists: %ld\n", found);
    return found ? 1 : 0;
}
