// prefix_sa.c -- simulated annealing over k-layer prefixes on n channels, minimizing |outputs|.
// Layer 1 is fixed to (0,1),(2,3),...; layers 2..k are matchings of standard comparators.
// Usage: prefix_sa n k iters seed [T0]
// Prints the best prefix as JSON: {"n":..,"outputs":..,"layers":[[[i,j],..],..]}
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAXN 20
static int n, K;
static unsigned *stamp;
static unsigned cur_stamp = 0;
static unsigned *bufA, *bufB;
static unsigned *L1out; static int L1cnt;

typedef struct { int p[MAXN + 1][MAXN]; } Prefix;   // p[t][k] = partner of k in layer t, -1 idle

static unsigned long long rng_state;
static inline unsigned long long rnd(void) {
    rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17; return rng_state;
}
static inline double urand(void) { return (rnd() >> 11) * (1.0 / 9007199254740992.0); }

static int apply_layer(const int *p, const unsigned *in, int cnt, unsigned *out) {
    int pairs_i[MAXN], pairs_j[MAXN], m = 0;
    for (int k = 0; k < n; k++) if (p[k] > k) { pairs_i[m] = k; pairs_j[m] = p[k]; m++; }
    cur_stamp++;
    int oc = 0;
    for (int a = 0; a < cnt; a++) {
        unsigned x = in[a];
        for (int c = 0; c < m; c++) {
            unsigned bi = (x >> pairs_i[c]) & 1, bj = (x >> pairs_j[c]) & 1;
            if (bi && !bj) x ^= (1u << pairs_i[c]) | (1u << pairs_j[c]);
        }
        if (stamp[x] != cur_stamp) { stamp[x] = cur_stamp; out[oc++] = x; }
    }
    return oc;
}

static int cost(const Prefix *P) {
    int cnt = L1cnt;
    memcpy(bufA, L1out, sizeof(unsigned) * cnt);
    unsigned *in = bufA, *out = bufB;
    for (int t = 1; t < K; t++) {
        cnt = apply_layer(P->p[t], in, cnt, out);
        unsigned *tmp = in; in = out; out = tmp;
    }
    return cnt;
}

static void mutate(Prefix *P) {
    int t = 1 + rnd() % (K - 1);
    int *p = P->p[t];
    int mv = rnd() % 4;
    int a = rnd() % n, b = rnd() % n;
    if (a == b) return;
    if (mv == 0) {                       // remove a's comparator
        if (p[a] >= 0) { p[p[a]] = -1; p[a] = -1; }
    } else if (mv == 1) {                // connect a and b (dropping their partners)
        if (p[a] >= 0) { p[p[a]] = -1; }
        if (p[b] >= 0) { p[p[b]] = -1; }
        p[a] = b; p[b] = a;
    } else if (mv == 2) {                // rewire: (a,pa),(b,pb) -> (a,b),(pa,pb)
        int pa = p[a], pb = p[b];
        if (pa < 0 || pb < 0 || pa == b) return;
        p[a] = b; p[b] = a; p[pa] = pb; p[pb] = pa;
    } else {                             // swap partner: (a,pa) -> (a,b) if b idle
        if (p[b] >= 0) return;
        if (p[a] >= 0) p[p[a]] = -1;
        p[a] = b; p[b] = a;
    }
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: prefix_sa n k iters seed [T0]\n"); return 1; }
    n = atoi(argv[1]); K = atoi(argv[2]);
    long iters = atol(argv[3]); rng_state = 0x9E3779B97F4A7C15ULL ^ (unsigned long long)atoll(argv[4]);
    double T0 = argc > 5 ? atof(argv[5]) : 20.0;
    stamp = calloc(1u << n, sizeof(unsigned));
    bufA = malloc(sizeof(unsigned) << n); bufB = malloc(sizeof(unsigned) << n); L1out = malloc(sizeof(unsigned) << n);
    // outputs of layer 1
    {
        int p1[MAXN]; for (int k = 0; k < n; k++) p1[k] = -1;
        for (int k = 0; k + 1 < n; k += 2) { p1[k] = k + 1; p1[k + 1] = k; }
        unsigned *all = malloc(sizeof(unsigned) << n);
        for (unsigned x = 0; x < (1u << n); x++) all[x] = x;
        L1cnt = apply_layer(p1, all, 1 << n, L1out);
        free(all);
    }
    Prefix P, best;
    for (int t = 0; t < K; t++) for (int k = 0; k < n; k++) P.p[t][k] = -1;
    for (int k = 0; k + 1 < n; k += 2) { P.p[0][k] = k + 1; P.p[0][k + 1] = k; }
    for (int t = 1; t < K; t++) {        // random initial maximal matchings
        int perm[MAXN]; for (int k = 0; k < n; k++) perm[k] = k;
        for (int k = n - 1; k > 0; k--) { int r = rnd() % (k + 1); int tmp = perm[k]; perm[k] = perm[r]; perm[r] = tmp; }
        for (int k = 0; k + 1 < n; k += 2) { P.p[t][perm[k]] = perm[k + 1]; P.p[t][perm[k + 1]] = perm[k]; }
    }
    int c = cost(&P), bc = c; best = P;
    for (long it = 0; it < iters; it++) {
        double T = T0 * (1.0 - (double)it / iters) + 1e-3;
        Prefix Q = P;
        mutate(&Q);
        int cq = cost(&Q);
        if (cq <= c || urand() < exp((c - cq) / T)) {
            P = Q; c = cq;
            if (c < bc) { bc = c; best = P; }
        }
    }
    printf("{\"n\": %d, \"outputs\": %d, \"layers\": [", n, bc);
    for (int t = 0; t < K; t++) {
        printf("%s[", t ? ", " : "");
        int first = 1;
        for (int k = 0; k < n; k++) if (best.p[t][k] > k) { printf("%s[%d, %d]", first ? "" : ", ", k, best.p[t][k]); first = 0; }
        printf("]");
    }
    printf("]}\n");
    return 0;
}
