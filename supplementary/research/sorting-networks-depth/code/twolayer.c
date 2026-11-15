/* Exact two-layer minimum: min over maximal layers M1,M of |L_M(Fix(M1))|,
   then the exact third-step ratio min over M3 from that F2. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int n, NS, nPairs, e, nLay, W;
static int pa[512], pb[512];
static int *lay;
static uint16_t *act;
static int cur[16], nc;

static int counting=1;
static void emit(void){
    if(!counting) for(int i=0;i<e;i++) lay[(size_t)nLay*e+i] = cur[i];
    nLay++;
}
static void gen(int start,int np,int used){
    if(np==e){ emit(); return; }
    for(int i=start;i<nPairs;i++){
        int a=pa[i], b=pb[i];
        if((used>>a)&1) continue;
        if((used>>b)&1) continue;
        cur[nc++]=i;
        gen(i+1,np+1, used|(1<<a)|(1<<b));
        nc--;
    }
}
static int pairs_of(int l,int t){ return lay[(size_t)l*e+t]; }

int main(int argc,char**argv){
    n=atoi(argv[1]);
    NS=1<<n; W=(NS+63)/64;
    nPairs=0;
    for(int i=0;i<n;i++) for(int j=i+1;j<n;j++){ pa[nPairs]=i; pb[nPairs]=j; nPairs++; }
    e=n/2;
    /* count layers */
    counting=1; nLay=0; nc=0; gen(0,0,0);
    lay=malloc((size_t)nLay*e*sizeof(int));
    counting=0; nLay=0; nc=0; gen(0,0,0);
    fprintf(stderr,"n=%d: %d pairs, e=%d, %d maximal layers, %d bitmap words\n",n,nPairs,e,nLay,W);

    act=malloc((size_t)nLay*NS*sizeof(uint16_t));
    for(int l=0;l<nLay;l++){
        uint16_t *A=act+(size_t)l*NS;
        for(int s=0;s<NS;s++){
            int v=s;
            for(int t=0;t<e;t++){
                int pi=pairs_of(l,t), a=pa[pi], b=pb[pi];
                int va=(v>>a)&1, vb=(v>>b)&1;
                if(va==1&&vb==0) v=(v&~(1<<a))|(1<<b);
            }
            A[s]=(uint16_t)v;
        }
    }
    int *fix=malloc(NS*sizeof(int));
    uint64_t *bm=calloc(W,sizeof(uint64_t)), *bestF2=calloc(W,sizeof(uint64_t));
    int best=NS+1,bestM1=-1,bestM=-1, hits=0, nf1=0;
    for(int l1=0;l1<nLay;l1++){
        int nf=0;
        for(int s=0;s<NS;s++){
            int ok=1;
            for(int t=0;t<e;t++){ int pi=pairs_of(l1,t),a=pa[pi],b=pb[pi];
                if(((s>>a)&1)==1&&((s>>b)&1)==0){ ok=0;break; } }
            if(ok) fix[nf++]=s;
        }
        if(l1==0) nf1=nf;
        for(int l=0;l<nLay;l++){
            memset(bm,0,W*sizeof(uint64_t));
            int c=0,pruned=0; uint16_t *A=act+(size_t)l*NS;
            for(int t=0;t<nf;t++){
                int u=A[fix[t]];
                if(!((bm[u>>6]>>(u&63))&1)){ bm[u>>6]|=1ULL<<(u&63); c++; }
                if(best<NS+1 && c>=best){ pruned=1; break; }
            }
            if(pruned) continue;
            if(c<best){ best=c;bestM1=l1;bestM=l;hits=1; memcpy(bestF2,bm,W*sizeof(uint64_t)); }
            else if(c==best) hits++;
        }
    }
    printf("n=%d: |Fix(M1)|=%d,  min over M of |L_M(Fix(M1))| = %d  (ratio %.4f), attained %d times\n",
           n,nf1,best,(double)best/nf1,hits);
    printf("   value histogram of |L_M(Fix(M1))| over all (M1,M):\n");
    { int mx=NS+1; long *h=calloc(mx,sizeof(long));
      for(int l1=0;l1<nLay;l1++){
        int nf=0; for(int s=0;s<NS;s++){ int ok=1;
            for(int t=0;t<e;t++){int pi=pairs_of(l1,t),a=pa[pi],b=pb[pi];
                if(((s>>a)&1)==1&&((s>>b)&1)==0){ok=0;break;}}
            if(ok) fix[nf++]=s; }
        for(int l=0;l<nLay;l++){ memset(bm,0,W*sizeof(uint64_t)); int c=0; uint16_t *A=act+(size_t)l*NS;
            for(int t=0;t<nf;t++){ int u=A[fix[t]];
                if(!((bm[u>>6]>>(u&63))&1)){ bm[u>>6]|=1ULL<<(u&63); c++; } }
            h[c]++; }
      }
      for(int v=0;v<=NS;v++) if(h[v]) printf("     %4d : %ld\n",v,h[v]);
      free(h); }
    printf("   best M1 = "); for(int t=0;t<e;t++){int pi=pairs_of(bestM1,t);printf("(%d,%d)",pa[pi]+1,pb[pi]+1);} printf("\n");
    printf("   best M  = "); for(int t=0;t<e;t++){int pi=pairs_of(bestM,t);printf("(%d,%d)",pa[pi]+1,pb[pi]+1);} printf("\n");
    { int *F2=malloc(NS*sizeof(int)); int nf2=0;
      for(int s=0;s<NS;s++) if((bestF2[s>>6]>>(s&63))&1) F2[nf2++]=s;
      int b3=NS+1,b3l=-1;
      for(int l=0;l<nLay;l++){
        memset(bm,0,W*sizeof(uint64_t)); int c=0; uint16_t *A=act+(size_t)l*NS;
        for(int t=0;t<nf2;t++){ int u=A[F2[t]];
            if(!((bm[u>>6]>>(u&63))&1)){ bm[u>>6]|=1ULL<<(u&63); c++; }
            if(b3<NS+1 && c>=b3) break; }
        if(c<b3){ b3=c; b3l=l; }
      }
      printf("   third step: |F_2|=%d, min over M3 of |F_3| = %d  (ratio %.4f)\n",nf2,b3,(double)b3/nf2);
      printf("   best M3 = "); for(int t=0;t<e;t++){int pi=pairs_of(b3l,t);printf("(%d,%d)",pa[pi]+1,pb[pi]+1);} printf("\n");
    }
    return 0;
}
