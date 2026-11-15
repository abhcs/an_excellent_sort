/* Exact min |F_t| by BFS over DISTINCT image sets (deduplicated), for n=9.
   Reports the number of distinct images and the minimum size at each level. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int n,NS,e,nLay,W;
static int pa[512],pb[512],nPairs;
static int *lay,*cur; static int nc;
static uint16_t *act;
static int counting=1;
static void emit(void){ if(!counting) for(int i=0;i<e;i++) lay[(size_t)nLay*e+i]=cur[i]; nLay++; }
static void gen(int st,int np,int used){ if(np==e){emit();return;}
  for(int i=st;i<nPairs;i++){int a=pa[i],b=pb[i];
    if((used>>a)&1)continue; if((used>>b)&1)continue;
    cur[nc++]=i; gen(i+1,np+1,used|(1<<a)|(1<<b)); nc--;}}
static int P(int l,int t){ return lay[(size_t)l*e+t]; }
/* hash set of images: each image is W uint64 words */
static uint64_t *tab; static char *occ; static size_t cap,used_;
static uint64_t hsh(const uint64_t*x){ uint64_t h=1469598103934665603ULL;
    for(int i=0;i<W;i++){ h^=x[i]; h*=1099511628211ULL; } return h; }
static void hs_init(size_t c){ free(tab); free(occ); cap=c; tab=calloc(cap*W,sizeof(uint64_t)); occ=calloc(cap,1); used_=0; }
static int hs_add(const uint64_t*x){
    size_t i=hsh(x)%cap;
    while(1){
        uint64_t *slot=tab+i*W;
        if(!occ[i]){ memcpy(slot,x,W*sizeof(uint64_t)); occ[i]=1; used_++; return 1; }
        if(memcmp(slot,x,W*sizeof(uint64_t))==0) return 0;
        i=(i+1)%cap;
    }
}
int main(int argc,char**argv){
    n=atoi(argv[1]); int TMAX=atoi(argv[2]);
    NS=1<<n; W=(NS+63)/64; nPairs=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){pa[nPairs]=i;pb[nPairs]=j;nPairs++;}
    e=n/2; cur=calloc(64,sizeof(int)); counting=1;nLay=0;nc=0;gen(0,0,0);
    lay=malloc((size_t)nLay*e*sizeof(int));
    counting=0;nLay=0;nc=0;gen(0,0,0);
    act=malloc((size_t)nLay*NS*sizeof(uint16_t));
    for(int l=0;l<nLay;l++){uint16_t*A=act+(size_t)l*NS;
        for(int s=0;s<NS;s++){int v=s;
            for(int t=0;t<e;t++){int pi=P(l,t),a=pa[pi],b=pb[pi];
                if(((v>>a)&1)==1&&((v>>b)&1)==0)v=(v&~(1<<a))|(1<<b);} A[s]=(uint16_t)v;}}
    fprintf(stderr,"n=%d: %d layers\n",n,nLay);
    size_t CAP=1<<22; hs_init(CAP);
    uint64_t *img=calloc(W,sizeof(uint64_t)), *lst=0; size_t nlst=0;
    /* level 1 */
    for(int l=0;l<nLay;l++){
        memset(img,0,W*sizeof(uint64_t));
        uint16_t*A=act+(size_t)l*NS;
        for(int s=0;s<NS;s++){int u=A[s]; img[u>>6]|=1ULL<<(u&63);}
        hs_add(img);
    }
    fprintf(stdout,"level 1: %zu distinct images\n",used_);
    for(int t=2;t<=TMAX;t++){
        /* snapshot current set */
        nlst=used_; lst=malloc(nlst*W*sizeof(uint64_t));
        size_t k=0; for(size_t i=0;i<cap;i++) if(occ[i]){ memcpy(lst+k*W,tab+i*W,W*sizeof(uint64_t)); k++; }
        hs_init(CAP*2>CAP?CAP*2:CAP);            /* grow */
        int minpop=NS+1;
        int *members=malloc(NS*sizeof(int));
        uint64_t *newimg=calloc(W,sizeof(uint64_t));
        for(size_t ii=0;ii<nlst;ii++){
            uint64_t *F=lst+ii*W; int nf=0;
            for(int s=0;s<NS;s++) if((F[s>>6]>>(s&63))&1) members[nf++]=s;
            for(int l=0;l<nLay;l++){
                memset(newimg,0,W*sizeof(uint64_t)); uint16_t*A=act+(size_t)l*NS;
                for(int q=0;q<nf;q++){int u=A[members[q]]; newimg[u>>6]|=1ULL<<(u&63);}
                hs_add(newimg);
            }
        }
        for(size_t i=0;i<cap;i++) if(occ[i]){ int pc=0;
            for(int w=0;w<W;w++) pc+=__builtin_popcountll(tab[i*W+w]);
            if(pc<minpop) minpop=pc; }
        free(members); free(newimg); free(lst);
        fprintf(stdout,"level %d: %zu distinct images, min |F_%d| = %d\n",t,used_,t,minpop);
        fflush(stdout);
    }
    return 0;
}
