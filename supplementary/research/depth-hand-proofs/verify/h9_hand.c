/* h9_hand.c -- exhaustive checks of the hand proofs in h9.md section 7 (nine classes of L2).
 *
 * Nine channels, L1 = (0,1)(2,3)(4,5), channels 6,7,8 idle.  A "placement" puts one infinity on each
 * pair of L1 (-inf on 2k or +inf on 2k+1); it is good for L2 if no comparator of L2 meets two reals.
 *  1. Lemma 11 (exchange): for every configuration with 2..5 infinities, every exchange (an infinity on x
 *     and a real on y, against a real on x and an infinity of either sign on y) and every one of the
 *     2620 layers: the two results are equal exactly when the signs agree and (x,y) is a comparator of
 *     the layer, and otherwise differ by an exchange with the same signs.
 *  2. For each class: the good placements after layer 2 are the ones listed in h9.md, and for every
 *     pair of matchings L3, L4 (sharing no comparator, for the classes marked so) the argument of
 *     h9.md goes through: some good placement whose six reals are paired up neither by L3 (after
 *     layer 2) nor by L4 (after layer 3), or else the named four-infinity placement gives reals that
 *     meet in at most one of layers 1-4, or in two of them with one comparator each.
 * Exit status 0 iff everything holds.  usage: h9_hand */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define N 9
#define NM 2620
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
/* a configuration: v[c] = -1 (-inf), 0 (real), +1 (+inf).  Infinities move; two reals never move apart. */
static int layer(int *v, const match_t *M) {      /* returns the number of comparators meeting two reals */
    int rr = 0;
    for (int e = 0; e < M->m; e++) {
        int a = M->a[e], b = M->b[e];
        if (!v[a] && !v[b]) { rr++; continue; }
        if (v[a] > v[b]) { int t = v[a]; v[a] = v[b]; v[b] = t; }
    }
    return rr;
}
static int reals(const int *v) { int R = 0; for (int c = 0; c < N; c++) if (!v[c]) R |= 1 << c; return R; }
static int pairs_up(const match_t *M, int R) {
    int cov = 0;
    for (int e = 0; e < M->m; e++) if ((R >> M->a[e] & 1) && (R >> M->b[e] & 1)) cov |= 1 << M->a[e] | 1 << M->b[e];
    return cov == R;
}
static int has(const match_t *M, int a, int b) { for (int e = 0; e < M->m; e++) if (M->a[e] == a && M->b[e] == b) return 1; return 0; }
static int shares(const match_t *X, const match_t *Y) { for (int e = 0; e < Y->m; e++) if (has(X, Y->a[e], Y->b[e])) return 1; return 0; }
static void parse(const char *s, match_t *M) {
    int a, b, n; M->m = 0;
    while (sscanf(s, "(%d,%d)%n", &a, &b, &n) == 2) { M->a[M->m] = a; M->b[M->m] = b; M->m++; s += n; }
}
static void inputs(const char *s, int *v) {     /* "+0 -1 ..." -> input configuration */
    int n, c; char sg; memset(v, 0, sizeof(int) * N);
    while (sscanf(s, " %c%d%n", &sg, &c, &n) == 2) { v[c] = sg == '+' ? 1 : -1; s += n; }
}
/* a four-infinity certificate: reals meet in at most one of layers 1-4, or in two with one comparator each */
static int certificate(const char *place, const match_t *const *L) {
    int v[N], nz = 0, ones = 1; inputs(place, v);
    for (int t = 0; t < 4; t++) { int c = layer(v, L[t]); if (c) { nz++; if (c != 1) ones = 0; } }
    return nz <= 1 || (nz == 2 && ones);
}

int main(void) {
    gen(0, 0);
    int ok = 1;
    /* ---- 1. exchange lemma ---- */
    long cases = 0, bad = 0; int pw[10]; pw[0] = 1; for (int i = 1; i < 10; i++) pw[i] = pw[i - 1] * 3;
    for (int code = 0; code < pw[9]; code++) {
        int v[N], ninf = 0;
        for (int c = 0; c < N; c++) { v[c] = code / pw[c] % 3 - 1; if (v[c]) ninf++; }
        if (ninf < 2 || ninf > 5) continue;
        for (int x = 0; x < N; x++) if (v[x]) for (int y = 0; y < N; y++) if (!v[y]) for (int s = -1; s <= 1; s += 2)
            for (int j = 0; j < nall; j++) {
                int a[N], b[N]; memcpy(a, v, sizeof a); memcpy(b, v, sizeof b); b[x] = 0; b[y] = s;
                layer(a, &all[j]); layer(b, &all[j]);
                int same = !memcmp(a, b, sizeof a), u = -1, w = -1, good = 1;
                if ((v[x] == s) && (has(&all[j], x < y ? x : y, x < y ? y : x))) good = same;
                else {
                    for (int c = 0; c < N; c++) if (a[c] != b[c]) {
                        if (a[c] && !b[c] && u < 0) u = c; else if (!a[c] && b[c] && w < 0) w = c; else good = 0;
                    }
                    if (u < 0 || w < 0 || a[u] != v[x] || b[w] != s) good = 0;
                }
                cases++; if (!good) bad++;
            }
    }
    printf("Lemma 11 (exchange): %ld cases, %ld violations\n", cases, bad);
    if (bad) ok = 0;

    /* ---- 2. the classes ---- */
    struct { const char *L2, *after, *norep, *named3, *named4a, *named4b; } cls[] = {
        /* after = the good placements after layer 2, as listed in h9.md, in the order of the 8 sign choices */
        { "(0,2)",      "[-0 -2 -4] [-0 +1 -4] [-0 +3 -4] [-0 -2 +5] [-0 +1 +5] [-0 +3 +5]", "", 0, 0, 0 },
        { "(0,3)",      "[-0 -2 -4] [-0 +3 -4] [+1 +3 -4] [-0 -2 +5] [-0 +3 +5] [+1 +3 +5]", "", 0, 0, 0 },
        { "(0,2)(1,4)", "[-0 -1 -2] [-0 -1 +4] [-0 -1 +3] [-0 +4 +5]", "", 0, 0, 0 },
        { "(0,2)(1,5)", "[-0 -4 +5] [-0 -2 +5] [-0 +1 +5] [-0 +3 +5]", "", 0, 0, 0 },
        { "(0,3)(1,2)", "[-0 -1 -4] [+2 +3 -4] [-0 -1 +5] [+2 +3 +5]", "no repeats", 0, 0, 0 },
        { "(0,3)(1,4)", "[-0 -1 -2] [-0 -1 +3] [-1 +3 +4] [+3 +4 +5]", "", "+0 -1 -2 +4", 0, 0 },
        { "(0,6)",      "[-0 -2 -4] [-0 +3 -4] [-0 -2 +5] [-0 +3 +5]", "no repeats", "B3", "+0 +1 +2 -4", "+0 +1 +2 -3" },
    };
    match_t L1; parse("(0,1)(2,3)(4,5)", &L1);
    for (int ci = 0; ci < 7; ci++) {
        match_t L2; parse(cls[ci].L2, &L2);
        int conf[8][N], np = 0;
        char listed[256] = "";
        for (int c = 0; c < 8; c++) {
            int v[N] = {0};
            for (int k = 0; k < 3; k++) { if (c >> k & 1) v[2 * k + 1] = 1; else v[2 * k] = -1; }
            if (layer(v, &L2)) continue;               /* (layer 1 cannot move these infinities) */
            memcpy(conf[np++], v, sizeof v);
            char buf[64] = "["; int f = 1;
            for (int ch = 0; ch < N; ch++) if (v[ch]) { char t[8]; sprintf(t, "%s%c%d", f ? "" : " ", v[ch] > 0 ? '+' : '-', ch); strcat(buf, t); f = 0; }
            strcat(buf, "]"); if (listed[0]) strcat(listed, " "); strcat(listed, buf);
        }
        int listed_ok = !strcmp(listed, cls[ci].after);
        long pairs = 0, viaT = 0, viaNamed = 0, fail = 0;
        int norep = cls[ci].norep[0] != 0;
        for (int j = 0; j < NM; j++) {
            int c3[8][N], inF3[8];
            for (int q = 0; q < np; q++) {
                inF3[q] = pairs_up(&all[j], reals(conf[q]));
                memcpy(c3[q], conf[q], sizeof c3[q]); layer(c3[q], &all[j]);
            }
            for (int k = 0; k < NM; k++) {
                if (norep && shares(&all[j], &all[k])) continue;
                pairs++;
                int free_ = 0;
                for (int q = 0; q < np && !free_; q++) if (!inF3[q] && !pairs_up(&all[k], reals(c3[q]))) free_ = 1;
                if (free_) { viaT++; continue; }
                const match_t *L[4] = { &L1, &L2, &all[j], &all[k] };
                int done = 0;
                if (cls[ci].named3 && !strcmp(cls[ci].named3, "B3")) {
                    /* (0,6): L3 = (b,c)(b',c')(1,i)(j,k); i != 6: +inf on 1 and 6, B, C infinities on b', c */
                    if (!has(&all[j], 1, 6)) done = certificate(has(&all[j], 2, 4) ? "+1 +6 +3 -4" : "+1 +6 +3 +5", L);
                    else done = certificate(has(&all[j], 2, 4) ? cls[ci].named4a : cls[ci].named4b, L);
                } else if (cls[ci].named3) done = certificate(cls[ci].named3, L);
                if (done) viaNamed++; else fail++;
            }
        }
        printf("L2 = %-10s placements after layer 2 %s (%s); %ld (L3,L4)%s: %ld by three infinities, "
               "%ld by the named placement, %ld not covered\n", cls[ci].L2, listed, listed_ok ? "as listed" : "NOT as listed",
               pairs, norep ? " sharing no comparator" : "", viaT, viaNamed, fail);
        if (!listed_ok || fail) ok = 0;
    }
    printf(ok ? "all hand-proof claims hold\n" : "SOME CLAIM FAILS\n");
    return ok ? 0 : 1;
}
