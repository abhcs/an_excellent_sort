/* Greedy descending chain: minimise |F_2| over all (M1,M2), then at each further
   step choose the layer minimising the image size.  Produces a valid t-layer
   network, so its value is an UPPER bound on min |F_t|. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int n,NS,nPairs,e,nLay,W;
static int pa[512],pb[512]; static int *lay; static uint16_t *act; static int cur[16],nc;
static int counting=1;
static void emit(void){ if(!counting) for(int i=0;i<e;i++) lay[(size_t)nLay*e+i]=cur[i]; nLay++; }
static void gen(int st,int np,int used){ if(np==e){emit();return;}
  for(int i=st;i<nPairs;i++){ int a=pa[i],b=pb[i];
    if((used>>a)&1)continue; if((used>>b)&1)continue;
    cur[nc++]=i; gen(i+1,np+1,used|(1<<a)|(1<<b)); nc--; } }
static int P(int l,int t){ return lay[(size_t)l*e+t]; }
static int count_img(int l,const int*S,int nS,uint64_t*bm){
    memset(bm,0,W*sizeof(uint64_t)); int c=0; uint16_t*A=act+(size_t)l*NS;
    for(int t=0;t<nS;t++){ int u=A[S[t]]; if(!((bm[u>>6]>>(u&63))&1)){bm[u>>6]|=1ULL<<(u&63);c++;} }
    return c; }
int main(int argc,char**argv){
    n=atoi(argv[1]); int T=atoi(argv[2]);
    NS=1<<n; W=(NS+63)/64; nPairs=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){pa[nPairs]=i;pb[nPairs]=j;nPairs++;}
    e=n/2; counting=1;nLay=0;nc=0;gen(0,0,0);
    lay=malloc((size_t)nLay*e*sizeof(int)); counting=0;nLay=0;nc=0;gen(0,0,0);
    act=malloc((size_t)nLay*NS*sizeof(uint16_t));
    for(int l=0;l<nLay;l++){uint16_t*A=act+(size_t)l*NS;
        for(int s=0;s<NS;s++){int v=s;
            for(int t=0;t<e;t++){int pi=P(l,t),a=pa[pi],b=pb[pi];
                if(((v>>a)&1)==1&&((v>>b)&1)==0)v=(v&~(1<<a))|(1<<b);} A[s]=(uint16_t)v;}}
    /* fix(M1) */
    int *fix=malloc(NS*sizeof(int)), *S=malloc(NS*sizeof(int));
    uint64_t *bm=calloc(W,sizeof(uint64_t)), *bestB=calloc(W,sizeof(uint64_t));
    int best=NS+1,b1=-1,b2=-1, nf1=0;
    for(int l1=0;l1<nLay;l1++){
        int nf=0;
        for(int s=0;s<NS;s++){int ok=1;
            for(int t=0;t<e;t++){int pi=P(l1,t),a=pa[pi],b=pb[pi];
                if(((s>>a)&1)==1&&((s>>b)&1)==0){ok=0;break;}}
            if(ok)fix[nf++]=s;}
        if(l1==0)nf1=nf;
        for(int l=0;l<nLay;l++){
            memset(bm,0,W*sizeof(uint64_t)); int c=0,pr=0; uint16_t*A=act+(size_t)l*NS;
            for(int t=0;t<nf;t++){int u=A[fix[t]];
                if(!((bm[u>>6]>>(u&63))&1)){bm[u>>6]|=1ULL<<(u&63);c++;}
                if(best<NS+1&&c>=best){pr=1;break;}}
            if(pr)continue;
            if(c<best){best=c;b1=l1;b2=l;memcpy(bestB,bm,W*sizeof(uint64_t));}
        }
    }
    printf("n=%d: |F_1|=%d  min|F_2|=%d (ratio %.4f)\n",n,nf1,best,(double)best/nf1);
    printf("  M1="); for(int t=0;t<e;t++){int pi=P(b1,t);printf("(%d,%d)",pa[pi]+1,pb[pi]+1);} printf("\n");
    printf("  M2="); for(int t=0;t<e;t++){int pi=P(b2,t);printf("(%d,%d)",pa[pi]+1,pb[pi]+1);} printf("\n");
    /* greedy descent */
    int nS=0; for(int s=0;s<NS;s++) if((bestB[s>>6]>>(s&63))&1) S[nS++]=s;
    int prev=nS;
    for(int step=3; step<=T; step++){
        int bb=NS+1,bl=-1;
        for(int l=0;l<nLay;l++){
            memset(bm,0,W*sizeof(uint64_t)); int c=0,pr=0; uint16_t*A=act+(size_t)l*NS;
            for(int t=0;t<nS;t++){int u=A[S[t]];
                if(!((bm[u>>6]>>(u&63))&1)){bm[u>>6]|=1ULL<<(u&63);c++;}
                if(bb<NS+1&&c>=bb){pr=1;break;}}
            if(pr)continue;
            if(c<bb){bb=c;bl=l;memcpy(bestB,bm,W*sizeof(uint64_t));}
        }
        nS=0; for(int s=0;s<NS;s++) if((bestB[s>>6]>>(s&63))&1) S[nS++]=s;
        printf("  |F_%d|=%d (ratio %.4f)   M%d=",step,nS,(double)nS/prev,step);
        for(int t=0;t<e;t++){int pi=P(bl,t);printf("(%d,%d)",pa[pi]+1,pb[pi]+1);} printf("\n");
        prev=nS;
    }
    return 0;
}
