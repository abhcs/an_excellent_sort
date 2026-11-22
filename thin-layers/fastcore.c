/* fastcore.c -- compiled helpers for the sentinel prover (README §8.11).

   Sets of 0/1 vectors on n <= 20 channels are sorted arrays of uint32 (bit k = channel k); inside,
   they are bitmaps of 2^n bits. A layer is an array of 2m ints i0, j0, i1, j1, ... (i < j: the
   minimum goes to i). Nothing here decides a proof step: the prover uses these functions to search,
   and check_facts.py re-checks every step (its symmetry rule in Python).

   Build: clang -O3 -shared -fPIC -o fastcore.dylib fastcore.c  (fastcore.py does it when needed). */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef uint32_t u32;
typedef uint64_t u64;

static inline u64 mix64(u64 x) {               /* splitmix64 finalizer */
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}

static inline u32 apply1(u32 x, const int *L, int m) {
    for (int c = 0; c < m; c++) {
        int i = L[2 * c], j = L[2 * c + 1];
        if (((x >> i) & 1) && !((x >> j) & 1)) x ^= (1u << i) | (1u << j);
    }
    return x;
}

static int bitmap_to_array(const u64 *bm, int words, u32 *out) {
    int k = 0;
    for (int w = 0; w < words; w++) {
        u64 b = bm[w];
        while (b) {
            int t = __builtin_ctzll(b);
            out[k++] = (u32)(w * 64 + t);
            b &= b - 1;
        }
    }
    return k;
}

/* outputs of all 2^n inputs through nl layers (sizes[l] comparators each, pairs concatenated) */
int fc_outputs(int n, int nl, const int *sizes, const int *pairs, u32 *out) {
    u32 N = 1u << n;
    int words = (int)((N + 63) / 64);
    u64 *bm = calloc((size_t)words, 8);
    for (u32 x = 0; x < N; x++) {
        u32 y = x;
        const int *p = pairs;
        for (int l = 0; l < nl; l++) {
            y = apply1(y, p, sizes[l]);
            p += 2 * sizes[l];
        }
        bm[y >> 6] |= 1ULL << (y & 63);
    }
    int k = bitmap_to_array(bm, words, out);
    free(bm);
    return k;
}

/* image of a set under one layer */
int fc_apply_layer(int n, const u32 *X, int nx, int m, const int *L, u32 *out) {
    u32 N = 1u << n;
    int words = (int)((N + 63) / 64);
    u64 *bm = calloc((size_t)words, 8);
    for (int a = 0; a < nx; a++) {
        u32 y = apply1(X[a], L, m);
        bm[y >> 6] |= 1ULL << (y & 63);
    }
    int k = bitmap_to_array(bm, words, out);
    free(bm);
    return k;
}

/* per channel: number of vectors with a 1 there, by weight (same numbers as chan_sigs in Python) */
void fc_chan_sigs(int n, const u32 *X, int nx, int *sig) {
    memset(sig, 0, sizeof(int) * (size_t)n * (size_t)(n + 1));
    for (int a = 0; a < nx; a++) {
        u32 x = X[a];
        int w = __builtin_popcount(x);
        while (x) {
            int i = __builtin_ctz(x);
            sig[i * (n + 1) + w]++;
            x &= x - 1;
        }
    }
}

/* channel pairs (i, j), i < j, that some vector has as 1 at i and 0 at j (the comparator can swap) */
int fc_nonredundant(int n, const u32 *X, int nx, int *out) {
    int k = 0;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) {
            for (int a = 0; a < nx; a++)
                if (((X[a] >> i) & 1) && !((X[a] >> j) & 1)) {
                    out[2 * k] = i;
                    out[2 * k + 1] = j;
                    k++;
                    break;
                }
        }
    return k;
}

/* ---------- relabeling search: sigma(A') = B, A' = A or its complement ---------- */

typedef struct {
    int n, m;
    const u32 *A;            /* A' (already complemented if needed) */
    const u32 *B;
    const u64 *bmB;          /* bitmap of B */
    int cand[20][20], ncand[20], order[20];
    int sigma[20], used[20];
    u64 *kA, *kB;            /* keys per depth: (n + 1) * m each */
    long nodes, budget;
    int all;                 /* collect all solutions (automorphisms) */
    int comp;
    int *outp, *outc, maxg, ng;
    int over;
} Search;

static int verify_full(Search *s) {
    for (int a = 0; a < s->m; a++) {
        u32 x = s->A[a], y = 0;
        while (x) {
            int i = __builtin_ctz(x);
            y |= 1u << s->sigma[i];
            x &= x - 1;
        }
        if (!((s->bmB[y >> 6] >> (y & 63)) & 1)) return 0;
    }
    return 1;
}

static int rec(Search *s, int t) {
    if (t == s->n) {
        if (!verify_full(s)) return 0;
        if (!s->all) return 1;
        if (s->ng < s->maxg) {
            for (int i = 0; i < s->n; i++) s->outp[s->ng * s->n + i] = s->sigma[i];
            s->outc[s->ng] = s->comp;
            s->ng++;
            return 0;
        }
        s->over = 1;
        return 1;                            /* stop: the list is full */
    }
    if (++s->nodes > s->budget) {
        s->over = 2;
        return 1;
    }
    int i = s->order[t];
    const u64 *pa = s->kA + (size_t)t * s->m, *pb = s->kB + (size_t)t * s->m;
    u64 *na = s->kA + (size_t)(t + 1) * s->m, *nb = s->kB + (size_t)(t + 1) * s->m;
    for (int c = 0; c < s->ncand[i]; c++) {
        int j = s->cand[i][c];
        if (s->used[j]) continue;
        u64 ha = 0, hb = 0, xa = 0, xb = 0;
        for (int a = 0; a < s->m; a++) {
            na[a] = pa[a] * 2 + ((s->A[a] >> i) & 1);
            nb[a] = pb[a] * 2 + ((s->B[a] >> j) & 1);
            u64 ma = mix64(na[a]), mb = mix64(nb[a]);
            ha += ma; hb += mb;
            xa ^= mix64(ma); xb ^= mix64(mb);
        }
        if (ha != hb || xa != xb) continue;   /* the key multisets differ */
        s->used[j] = 1;
        s->sigma[i] = j;
        if (rec(s, t + 1)) return 1;
        s->used[j] = 0;
    }
    return 0;
}

static int cmp_rows(const int *a, const int *b, int len) {
    for (int k = 0; k < len; k++)
        if (a[k] != b[k]) return a[k] < b[k] ? -1 : 1;
    return 0;
}

/* one orientation: returns 1 when a relabeling was found (first one, or the list stops) */
static int search_one(int n, const u32 *A, int m, const u32 *B, const u64 *bmB, long budget, int all,
                      int comp, int *outp, int *outc, int maxg, int *ng, int *over, int *perm_out) {
    int len = n + 1;
    int *sa = malloc(sizeof(int) * n * len), *sb = malloc(sizeof(int) * n * len);
    fc_chan_sigs(n, A, m, sa);
    fc_chan_sigs(n, B, m, sb);
    /* the sorted rows must agree */
    int *ra = malloc(sizeof(int) * n), *rb = malloc(sizeof(int) * n);
    for (int i = 0; i < n; i++) ra[i] = rb[i] = i;
    for (int x = 1; x < n; x++)              /* insertion sort of row indices */
        for (int y = x; y > 0 && cmp_rows(sa + ra[y] * len, sa + ra[y - 1] * len, len) < 0; y--) {
            int tmp = ra[y]; ra[y] = ra[y - 1]; ra[y - 1] = tmp;
        }
    for (int x = 1; x < n; x++)
        for (int y = x; y > 0 && cmp_rows(sb + rb[y] * len, sb + rb[y - 1] * len, len) < 0; y--) {
            int tmp = rb[y]; rb[y] = rb[y - 1]; rb[y - 1] = tmp;
        }
    int ok = 1;
    for (int k = 0; k < n && ok; k++)
        if (cmp_rows(sa + ra[k] * len, sb + rb[k] * len, len) != 0) ok = 0;
    free(ra); free(rb);
    if (!ok) { free(sa); free(sb); return 0; }
    Search s;
    memset(&s, 0, sizeof(s));
    s.n = n; s.m = m; s.A = A; s.B = B; s.bmB = bmB; s.budget = budget; s.all = all; s.comp = comp;
    s.outp = outp; s.outc = outc; s.maxg = maxg; s.ng = *ng;
    for (int i = 0; i < n; i++) {
        s.ncand[i] = 0;
        for (int j = 0; j < n; j++)
            if (cmp_rows(sa + i * len, sb + j * len, len) == 0) s.cand[i][s.ncand[i]++] = j;
        s.order[i] = i;
    }
    free(sa); free(sb);
    for (int x = 1; x < n; x++)              /* fewest candidates first (stable) */
        for (int y = x; y > 0 && s.ncand[s.order[y]] < s.ncand[s.order[y - 1]]; y--) {
            int tmp = s.order[y]; s.order[y] = s.order[y - 1]; s.order[y - 1] = tmp;
        }
    s.kA = malloc(sizeof(u64) * (size_t)(n + 1) * (size_t)m);
    s.kB = malloc(sizeof(u64) * (size_t)(n + 1) * (size_t)m);
    for (int a = 0; a < m; a++) {
        s.kA[a] = (u64)__builtin_popcount(A[a]);
        s.kB[a] = (u64)__builtin_popcount(B[a]);
    }
    int stopped = rec(&s, 0);
    int found = !all && stopped && s.over == 0;   /* a stop with s.over set is the budget or a full list */
    if (found && perm_out)
        for (int i = 0; i < n; i++) perm_out[i] = s.sigma[i];
    *ng = s.ng;
    if (s.over) *over = s.over;
    free(s.kA); free(s.kB);
    return found;
}

static u64 *make_bitmap(int n, const u32 *X, int m) {
    u32 N = 1u << n;
    int words = (int)((N + 63) / 64);
    u64 *bm = calloc((size_t)words, 8);
    for (int a = 0; a < m; a++) bm[X[a] >> 6] |= 1ULL << (X[a] & 63);
    return bm;
}

/* 1 if B = sigma(A) or sigma(complement A); perm_out (n ints) and *comp_out receive the relabeling.
   0 if none, -1 if the budget ran out (treated as 'not equivalent' by the caller). */
int fc_equivalent(int n, const u32 *A, int na, const u32 *B, int nb, long budget, int *perm_out, int *comp_out) {
    if (na != nb) return 0;
    u32 mask = (n == 32) ? 0xffffffffu : ((1u << n) - 1);
    u64 *bmB = make_bitmap(n, B, nb);
    u32 *Ac = malloc(sizeof(u32) * (size_t)na);
    for (int a = 0; a < na; a++) Ac[a] = A[a] ^ mask;
    int ng = 0, over = 0, res = 0;
    for (int comp = 0; comp < 2 && !res; comp++) {
        res = search_one(n, comp ? Ac : A, na, B, bmB, budget, 0, comp, NULL, NULL, 0, &ng, &over, perm_out);
        if (res && comp_out) *comp_out = comp;
    }
    free(Ac); free(bmB);
    if (res) return 1;
    return over == 2 ? -1 : 0;
}

/* all relabelings g with g(X) = X (comp: X complemented first), up to maxg; returns their number,
   or -(number) if the list was cut off (by maxg or the budget). The identity is included. */
int fc_automorphisms(int n, const u32 *X, int nx, int maxg, long budget, int *perms, int *comps) {
    u32 mask = (1u << n) - 1;
    u64 *bm = make_bitmap(n, X, nx);
    u32 *Xc = malloc(sizeof(u32) * (size_t)nx);
    for (int a = 0; a < nx; a++) Xc[a] = X[a] ^ mask;
    int ng = 0, over = 0;
    for (int comp = 0; comp < 2; comp++) {
        int o = 0;
        search_one(n, comp ? Xc : X, nx, X, bm, budget, 1, comp, perms, comps, maxg, &ng, &o, NULL);
        if (o) over = o;
        if (over) break;
    }
    free(Xc); free(bm);
    return over ? -ng : ng;
}

/* ---------- canonical next layers ---------- */

/* a layer is a sorted list of pair codes i * 32 + j (i < j); one layer is smaller than another of
   the same size when its code list is lexicographically smaller. A layer is canonical when no listed
   relabeling maps it to a smaller one. */
typedef struct {
    int n, np, cap, ng;
    const int *pi, *pj;        /* candidate pairs, sorted by code */
    const int *perms;          /* ng * n */
    int cur[16], ncur;         /* indices into pairs */
    int *out;                  /* layers: for each, cap + 1 ints: size, then pair indices */
    long cnt, maxout;
} Enum;

static int canonical(Enum *e) {
    int m = e->ncur;
    int code[16], img[16];
    for (int c = 0; c < m; c++) code[c] = e->pi[e->cur[c]] * 32 + e->pj[e->cur[c]];
    for (int g = 0; g < e->ng; g++) {
        const int *s = e->perms + (size_t)g * e->n;
        for (int c = 0; c < m; c++) {
            int a = s[e->pi[e->cur[c]]], b = s[e->pj[e->cur[c]]];
            img[c] = a < b ? a * 32 + b : b * 32 + a;
        }
        for (int x = 1; x < m; x++)          /* insertion sort */
            for (int y = x; y > 0 && img[y] < img[y - 1]; y--) {
                int tmp = img[y]; img[y] = img[y - 1]; img[y - 1] = tmp;
            }
        for (int c = 0; c < m; c++) {
            if (img[c] < code[c]) return 0;
            if (img[c] > code[c]) break;
        }
    }
    return 1;
}

static void enum_rec(Enum *e, int start, u32 used) {
    if (e->ncur > 0 && canonical(e)) {
        if (e->cnt < e->maxout) {
            int *o = e->out + (size_t)e->cnt * (e->cap + 1);
            o[0] = e->ncur;
            for (int c = 0; c < e->ncur; c++) o[1 + c] = e->cur[c];
        }
        e->cnt++;
    }
    if (e->ncur == e->cap) return;
    for (int k = start; k < e->np; k++) {
        int i = e->pi[k], j = e->pj[k];
        if (((used >> i) & 1) || ((used >> j) & 1)) continue;
        e->cur[e->ncur++] = k;
        enum_rec(e, k + 1, used | (1u << i) | (1u << j));
        e->ncur--;
    }
}

/* pairs: np pairs (2 ints each), sorted by code. Writes canonical layers into out (maxout slots of
   cap + 1 ints) and returns their total number (which may exceed maxout: call again with room). */
long fc_canonical_layers(int n, int np, const int *pairs, int cap, int ng, const int *perms, long maxout, int *out) {
    Enum e;
    memset(&e, 0, sizeof(e));
    int *pi = malloc(sizeof(int) * (size_t)(np > 0 ? np : 1)), *pj = malloc(sizeof(int) * (size_t)(np > 0 ? np : 1));
    for (int k = 0; k < np; k++) { pi[k] = pairs[2 * k]; pj[k] = pairs[2 * k + 1]; }
    e.n = n; e.np = np; e.cap = cap; e.ng = ng; e.pi = pi; e.pj = pj; e.perms = perms;
    e.out = out; e.maxout = maxout;
    enum_rec(&e, 0, 0);
    free(pi); free(pj);
    return e.cnt;
}

/* ---------- child keys for a split ---------- */

/* For each layer (layers as above: size, then pair indices into pairs): the child Y = layer(X).
   keys[4 * l ..]: |Y|, two order-free hashes of Y (exact duplicates), and an invariant hash under
   relabeling and complement (from the per-channel weight counts; equal for equivalent children). */
static void sorted_rows(int n, const int *sig, int *rows) {
    int len = n + 1;
    int idx[20];
    for (int i = 0; i < n; i++) idx[i] = i;
    for (int x = 1; x < n; x++)
        for (int y = x; y > 0 && cmp_rows(sig + idx[y] * len, sig + idx[y - 1] * len, len) < 0; y--) {
            int tmp = idx[y]; idx[y] = idx[y - 1]; idx[y - 1] = tmp;
        }
    for (int i = 0; i < n; i++) memcpy(rows + i * len, sig + idx[i] * len, sizeof(int) * len);
}

void fc_child_keys(int n, const u32 *X, int nx, int np, const int *pairs, int cap, long nl, const int *layers, u64 *keys) {
    u32 N = 1u << n;
    int words = (int)((N + 63) / 64);
    int len = n + 1;
    u64 *bm = calloc((size_t)words, 8);
    u32 *Y = malloc(sizeof(u32) * (size_t)(nx > 0 ? nx : 1));
    int *sig = malloc(sizeof(int) * n * len), *sigc = malloc(sizeof(int) * n * len);
    int *ra = malloc(sizeof(int) * n * len), *rc = malloc(sizeof(int) * n * len);
    int L[32];
    for (long l = 0; l < nl; l++) {
        const int *lay = layers + (size_t)l * (cap + 1);
        int m = lay[0];
        for (int c = 0; c < m; c++) { L[2 * c] = pairs[2 * lay[1 + c]]; L[2 * c + 1] = pairs[2 * lay[1 + c] + 1]; }
        memset(bm, 0, (size_t)words * 8);
        for (int a = 0; a < nx; a++) {
            u32 y = apply1(X[a], L, m);
            bm[y >> 6] |= 1ULL << (y & 63);
        }
        int ny = bitmap_to_array(bm, words, Y);
        u64 h1 = 0, h2 = 0;
        int wc[21];
        memset(wc, 0, sizeof(wc));
        for (int a = 0; a < ny; a++) {
            u64 z = mix64((u64)Y[a] + 0x1234567ULL);
            h1 += z;
            h2 ^= mix64(z ^ 0xabcdefULL);
            wc[__builtin_popcount(Y[a])]++;
        }
        fc_chan_sigs(n, Y, ny, sig);
        /* complement: bit i is 1 where it was 0; weight n - w */
        for (int i = 0; i < n; i++)
            for (int w = 0; w <= n; w++)
                sigc[i * len + (n - w)] = wc[w] - sig[i * len + w];
        sorted_rows(n, sig, ra);
        sorted_rows(n, sigc, rc);
        const int *best = cmp_rows(ra, rc, n * len) <= 0 ? ra : rc;
        u64 inv = mix64((u64)ny);
        for (int k = 0; k < n * len; k++) inv = mix64(inv ^ (u64)(unsigned)best[k] ^ ((u64)k << 32));
        keys[4 * l] = (u64)ny;
        keys[4 * l + 1] = h1;
        keys[4 * l + 2] = h2;
        keys[4 * l + 3] = inv;
    }
    free(bm); free(Y); free(sig); free(sigc); free(ra); free(rc);
}

/* ---- quick covers (sprove.Prover._qcover) ----
   Next layers are closed greedily by sentinel sets, each listed once in the split step. A set closes
   a layer through a quick step if no comparator of the layer is one of the set's bad pairs (two real
   lines, one of them already at the top allowed level), or through a lemma step if the residual's
   layer profile with the layer added fits a lemma. The loop makes the same choices as the Python
   one: for a layer that no chosen set closes, the first 12 sets that close it are candidates and the
   one closing most of the next 400 layers is chosen. check_facts.py re-checks every closed layer. */
#define QMAXH 64
typedef struct {
    int n, t2;
    const int *hasbad; const u64 *bad;     /* bad pairs: 2 words per set */
    const u32 *real;                      /* channels holding a real line */
    const int *chlvl, *asap, *h, *r;      /* chlvl: n per set; asap: QMAXH per set */
    const int *lemoff, *lemcnt, *lem;     /* lemmas (d2, a2, m2) */
    const int *capoff, *caplen, *caps;    /* residual caps */
    int lp; const int *asis;              /* prefix length; real comparisons per prefix layer, lp per set */
} QC;

static int qcloses(const QC *q, int e, const int *L, int m, const u64 *lm) {
    if (q->hasbad[e] && !(q->bad[2 * e] & lm[0]) && !(q->bad[2 * e + 1] & lm[1])) return 1;
    int nlem = q->lemcnt[e];
    if (!nlem) return 0;
    int n = q->n, h = q->h[e], h2 = h, plen = h, prof[QMAXH];
    for (int l = 0; l < h; l++) prof[l] = q->asap[e * QMAXH + l];
    u32 real = q->real[e];
    const int *lv = q->chlvl + e * n;
    for (int c = 0; c < m; c++) {
        int i = L[2 * c], j = L[2 * c + 1];
        if (((real >> i) & 1) && ((real >> j) & 1)) {
            int v = (lv[i] > lv[j] ? lv[i] : lv[j]) + 1;
            while (plen < v) prof[plen++] = 0;
            prof[v - 1]++;
            if (v > h2) h2 = v;
        }
    }
    const int *lems = q->lem + 3 * q->lemoff[e], *cp = q->caps + q->capoff[e];
    int cl = q->caplen[e], r = q->r[e];
    for (int k = 0; k < nlem; k++) {
        int d2 = lems[3 * k], a2 = lems[3 * k + 1], m2 = lems[3 * k + 2], fits = 1;
        if (h2 + q->t2 > d2) continue;
        for (int l = 0; l < m2 && fits; l++) {
            int x = l < h2 ? prof[l] : (l - h2 < cl ? cp[l - h2] : r / 2);
            if (x > a2) fits = 0;
        }
        if (fits) return 1;
    }
    /* the residual in its own layers: lp prefix layers plus the next one, then the free layers */
    int hh = q->lp + 1, cnt = 0;
    for (int c = 0; c < m; c++) {
        int i = L[2 * c], j = L[2 * c + 1];
        if (((real >> i) & 1) && ((real >> j) & 1)) cnt++;
    }
    const int *ai = q->asis + e * q->lp;
    for (int k = 0; k < nlem; k++) {
        int d2 = lems[3 * k], a2 = lems[3 * k + 1], m2 = lems[3 * k + 2], fits = 1;
        if (hh + q->t2 > d2) continue;
        for (int l = 0; l < m2 && fits; l++) {
            int x = l < q->lp ? ai[l] : (l == q->lp ? cnt : (l - hh < cl ? cp[l - hh] : r / 2));
            if (x > a2) fits = 0;
        }
        if (fits) return 1;
    }
    return 0;
}

/* layers: nl slots of 1 + 2*cap ints (size, then channel pairs). chosen: room for ns set indices;
   open: one flag per layer. Returns the number of open layers. */
long fc_qcover(int n, int t2, int ns, const int *hasbad, const u64 *bad, const u32 *real, const int *chlvl,
               const int *asap, const int *h, const int *r, const int *lemoff, const int *lemcnt,
               const int *lem, const int *capoff, const int *caplen, const int *caps,
               int lp, const int *asis,
               long nl, int cap, const int *layers, int *chosen, int *nchosen, char *open) {
    QC q = {n, t2, hasbad, bad, real, chlvl, asap, h, r, lemoff, lemcnt, lem, capoff, caplen, caps, lp, asis};
    int pidx[32][32], k = 0;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) pidx[i][j] = k++;
    int w = 1 + 2 * cap;
    u64 *lm = calloc(2 * (size_t)(nl > 0 ? nl : 1), sizeof(u64));
    for (long l = 0; l < nl; l++) {
        const int *L = layers + l * w;
        for (int c = 0; c < L[0]; c++) {
            int p = pidx[L[1 + 2 * c]][L[2 + 2 * c]];
            lm[2 * l + (p >> 6)] |= 1ULL << (p & 63);
        }
    }
    int nch = 0;
    long nopen = 0;
    for (long l = 0; l < nl; l++) {
        const int *L = layers + l * w;
        int done = 0;
        open[l] = 0;
        for (int c = 0; c < nch && !done; c++)
            if (qcloses(&q, chosen[c], L + 1, L[0], lm + 2 * l)) done = 1;
        if (done) continue;
        int cands[12], nc = 0;
        for (int e = 0; e < ns && nc < 12; e++)
            if (qcloses(&q, e, L + 1, L[0], lm + 2 * l)) cands[nc++] = e;
        if (!nc) {
            open[l] = 1;
            nopen++;
            continue;
        }
        long wend = l + 401 < nl ? l + 401 : nl, bestcnt = -1;
        int best = cands[0];
        for (int c = 0; c < nc; c++) {
            long cnt = 0;
            for (long u = l + 1; u < wend; u++) {
                const int *L2 = layers + u * w;
                cnt += qcloses(&q, cands[c], L2 + 1, L2[0], lm + 2 * u);
            }
            if (cnt > bestcnt) { bestcnt = cnt; best = cands[c]; }
        }
        chosen[nch++] = best;
    }
    *nchosen = nch;
    free(lm);
    return nopen;
}
