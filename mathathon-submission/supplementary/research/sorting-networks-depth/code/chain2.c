/* Greedy descending chain starting from the brick pair (M1 adjacent, M2 crossing),
   without computing the exact 2-layer minimum.  For larger n. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int n,NS,nPairs,e,nLay,W;
static int pa[512],pb[512]; static int *lay; static uint16_t *act; static int cur[16],nc;
static int counting=1;
static void emit(void){ if(!counting) for(int i=0;i<e;i++) lay[(size_t)nLay*e+i]=cur[i]; nLay++; }
static void gen(int st,int np,int used){ if(np==e){emit();return;}
  for(int i=st;i<nPairs;i++){int a=pa[i],b=pb[i];
    if((used>>a)&1)continue; if((used>>b)&1)continue;
    cur[nc++]=i; gen(i+1,np+1,used|(1<<a)|(1<<b)); nc--;}}
static int P(int l,int t){ return lay[(size_t)l*e+t]; }
static int findlayer(int a,int b){ for(int l=0;l<nLay;l++) for(int t=0;t<e;t++){
    int pi=P(l,t); if(pa[pi]==a&&pb[pi]==b) { for(int u=0;u<e;u++){int pj=P(l,u);
        if(!((pa[pj]==a&&pb[pj]==b)||(pa[pj]==b&&pb[pj]==a))){} } } }
  /* simpler: linear scan over layers comparing pair sets */
  for(int l=0;l<nLay;l++){ int hit=0;
    for(int t=0;t<e;t++){ int pi=P(l,t); if(pa[pi]==a&&pb[pi]==b) hit=1; }
    if(hit){ int ok=1,c2=0;
      for(int t=0;t<e;t++){ int pi=P(l,t);
        if((pa[pi]==a&&pb[pi]==b)) c2++; }
      if(c2==1 && ok) return l; } }
  return -1;
}
int main(int argc,char**argv){
    n=atoi(argv[1]); int T=atoi(argv[2]);
    NS=1<<n; W=(NS+63)/64; nPairs=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){pa[nPairs]=i;pb[nPairs]=j;nPairs++;}
    e=n/2; counting=1;nLay=0;nc=0;gen(0,0,0);
    fprintf(stderr,"n=%d: %d layers\n",n,nLay);
    lay=malloc((size_t)nLay*e*sizeof(int)); counting=0;nLay=0;nc=0;gen(0,0,0);
    act=malloc((size_t)nLay*NS*sizeof(uint16_t));
    for(int l=0;l<nLay;l++){uint16_t*A=act+(size_t)l*NS;
        for(int s=0;s<NS;s++){int v=s;
            for(int t=0;t<e;t++){int pi=P(l,t),a=pa[pi],b=pb[pi];
                if(((v>>a)&1)==1&&((v>>b)&1)==0)v=(v&~(1<<a))|(1<<b);} A[s]=(uint16_t)v;}}
    /* brick start: M1 = adjacent pairs (1,2)(3,4)..., M2 = (1,3)(2,4)(5,7)(6,8)... */
    int *S=malloc(NS*sizeof(int));
    uint64_t *bm=calloc(W,sizeof(uint64_t)), *keep=calloc(W,sizeof(uint64_t));
    int nS=0;
    for(int s=0;s<NS;s++){ int ok=1;
        for(int t=0;t<e;t++){ int a=2*t,b=2*t+1;      /* 0-indexed adjacent */
            if(((s>>a)&1)==1&&((s>>b)&1)==0){ok=0;break;} }
        if(ok) S[nS++]=s; }
    printf("n=%d: |F_1| = %d\n",n,nS); int prev=nS;
    for(int step=2; step<=T; step++){
        int bb=NS+1,bl=-1;
        for(int l=0;l<nLay;l++){
            memset(bm,0,W*sizeof(uint64_t)); int c=0,pr=0; uint16_t*A=act+(size_t)l*NS;
            for(int t=0;t<nS;t++){int u=A[S[t]];
                if(!((bm[u>>6]>>(u&63))&1)){bm[u>>6]|=1ULL<<(u&63);c++;}
                if(bb<NS+1&&c>=bb){pr=1;break;}}
            if(pr)continue;
            if(c<bb){bb=c;bl=l;memcpy(keep,bm,W*sizeof(uint64_t));}
        }
        nS=0; for(int s=0;s<NS;s++) if((keep[s>>6]>>(s&63))&1) S[nS++]=s;
        printf("  |F_%d| = %d (ratio %.4f)   M%d = ",step,nS,(double)nS/prev,step);
        for(int t=0;t<e;t++){int pi=P(bl,t);printf("(%d,%d)",pa[pi]+1,pb[pi]+1);} printf("\n");
        fflush(stdout); prev=nS;
    }
    return 0;
}
