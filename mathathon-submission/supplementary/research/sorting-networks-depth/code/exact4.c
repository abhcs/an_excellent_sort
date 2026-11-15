/* Is min |F_4| <= LIMIT over all 4-layer maximal-layer networks? (decision, pruned) */
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
    n=atoi(argv[1]); int LIMIT=atoi(argv[2]);
    NS=1<<n; W=(NS+63)/64; nPairs=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){pa[nPairs]=i;pb[nPairs]=j;nPairs++;}
    e=n/2; counting=1;nLay=0;nc=0;gen(0,0,0);
    lay=malloc((size_t)nLay*e*sizeof(int)); counting=0;nLay=0;nc=0;gen(0,0,0);
    act=malloc((size_t)nLay*NS*sizeof(uint16_t));
    for(int l=0;l<nLay;l++){uint16_t*A=act+(size_t)l*NS;
        for(int s=0;s<NS;s++){int v=s;
            for(int t=0;t<e;t++){int pi=P(l,t),a=pa[pi],b=pb[pi];
                if(((v>>a)&1)==1&&((v>>b)&1)==0)v=(v&~(1<<a))|(1<<b);} A[s]=(uint16_t)v;}}
    uint64_t *bm=calloc(W,sizeof(uint64_t));
    int found=0, bestfound=NS+1;
    int *F1=malloc(NS*sizeof(int)),*F2=malloc(NS*sizeof(int)),*F3=malloc(NS*sizeof(int));
    for(int l1=0;l1<nLay;l1++){
        int n1=0;
        for(int s=0;s<NS;s++){int ok=1;
            for(int t=0;t<e;t++){int pi=P(l1,t),a=pa[pi],b=pb[pi];
                if(((s>>a)&1)==1&&((s>>b)&1)==0){ok=0;break;}}
            if(ok)F1[n1++]=s;}
        for(int l2=0;l2<nLay;l2++){
            int n2=0; memset(bm,0,W*sizeof(uint64_t)); uint16_t*A2=act+(size_t)l2*NS;
            for(int t=0;t<n1;t++){int u=A2[F1[t]];
                if(!((bm[u>>6]>>(u&63))&1)){bm[u>>6]|=1ULL<<(u&63);F2[n2++]=u;}}
            for(int l3=0;l3<nLay;l3++){
                int n3=0; memset(bm,0,W*sizeof(uint64_t)); uint16_t*A3=act+(size_t)l3*NS;
                for(int t=0;t<n2;t++){int u=A3[F2[t]];
                    if(!((bm[u>>6]>>(u&63))&1)){bm[u>>6]|=1ULL<<(u&63);F3[n3++]=u;}}
                for(int l4=0;l4<nLay;l4++){
                    memset(bm,0,W*sizeof(uint64_t)); int c=0,pr=0; uint16_t*A4=act+(size_t)l4*NS;
                    for(int t=0;t<n3;t++){int u=A4[F3[t]];
                        if(!((bm[u>>6]>>(u&63))&1)){bm[u>>6]|=1ULL<<(u&63);c++;}
                        if(c>LIMIT){pr=1;break;}}
                    if(!pr){found++; if(c<bestfound){bestfound=c;
                        printf("  |F_4| = %d  M1..M4 = ",c);
                        int ls[4]={l1,l2,l3,l4};
                        for(int q=0;q<4;q++){printf("[");for(int t=0;t<e;t++){int pi=P(ls[q],t);printf("(%d,%d)",pa[pi]+1,pb[pi]+1);}printf("]");}
                        printf("\n"); fflush(stdout);} }
                }
            }
        }
    }
    printf("n=%d: networks with |F_4| <= %d : %d ; best found = %d  => min |F_4| %s %d\n",
        n,LIMIT,found,bestfound, found? "is <=":"is >", found? LIMIT:LIMIT);
    return 0;
}
