/* Exact min |F_3| over all 3-layer maximal-layer networks (brute force). */
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
int main(int argc,char**argv){
    n=atoi(argv[1]);
    NS=1<<n; W=(NS+63)/64; nPairs=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){pa[nPairs]=i;pb[nPairs]=j;nPairs++;}
    e=n/2; counting=1;nLay=0;nc=0;gen(0,0,0);
    lay=malloc((size_t)nLay*e*sizeof(int)); counting=0;nLay=0;nc=0;gen(0,0,0);
    act=malloc((size_t)nLay*NS*sizeof(uint16_t));
    for(int l=0;l<nLay;l++){uint16_t*A=act+(size_t)l*NS;
        for(int s=0;s<NS;s++){int v=s;
            for(int t=0;t<e;t++){int pi=P(l,t),a=pa[pi],b=pb[pi];
                if(((v>>a)&1)==1&&((v>>b)&1)==0)v=(v&~(1<<a))|(1<<b);} A[s]=(uint16_t)v;}}
    int best=NS+1;
    uint64_t *bm=calloc(W,sizeof(uint64_t));
    for(int l1=0;l1<nLay;l1++){
        int *F1=malloc(NS*sizeof(int)),n1=0;
        for(int s=0;s<NS;s++){int ok=1;
            for(int t=0;t<e;t++){int pi=P(l1,t),a=pa[pi],b=pb[pi];
                if(((s>>a)&1)==1&&((s>>b)&1)==0){ok=0;break;}}
            if(ok)F1[n1++]=s;}
        for(int l2=0;l2<nLay;l2++){
            int *F2=malloc(NS*sizeof(int)),n2=0;
            memset(bm,0,W*sizeof(uint64_t)); uint16_t*A2=act+(size_t)l2*NS;
            for(int t=0;t<n1;t++){int u=A2[F1[t]];
                if(!((bm[u>>6]>>(u&63))&1)){bm[u>>6]|=1ULL<<(u&63);F2[n2++]=u;}}
            for(int l3=0;l3<nLay;l3++){
                memset(bm,0,W*sizeof(uint64_t)); int c=0,pr=0; uint16_t*A3=act+(size_t)l3*NS;
                for(int t=0;t<n2;t++){int u=A3[F2[t]];
                    if(!((bm[u>>6]>>(u&63))&1)){bm[u>>6]|=1ULL<<(u&63);c++;}
                    if(best<NS+1&&c>=best){pr=1;break;}}
                if(!pr&&c<best)best=c;
            }
            free(F2);
        }
        free(F1);
    }
    printf("n=%d: EXACT min |F_3| over all 3-layer maximal-layer networks = %d\n",n,best);
    return 0;
}
