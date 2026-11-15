#include <math.h>
/* Sampled rho_6: min over RANDOM connected pairs (M1,M2) of perfect matchings on 12
   channels of |L_M2(Fix(M1))|/|Fix(M1)|.  An upper bound on rho_6. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int n,NS,e,W,nPairs;
static int pa[256],pb[256];
static uint32_t seed=987654321u;
static uint32_t rnd(void){ seed^=seed<<13; seed^=seed>>17; seed^=seed<<5; return seed; }
static void randpm(int*L){
    int ch[16]; for(int i=0;i<n;i++) ch[i]=i;
    for(int i=n-1;i>0;i--){ int j=rnd()%(i+1); int t=ch[i];ch[i]=ch[j];ch[j]=t; }
    for(int q=0;q<e;q++){ int a=ch[2*q],b=ch[2*q+1]; if(a>b){int t=a;a=b;b=t;} L[2*q]=a;L[2*q+1]=b; }
}
static int connected(const int*A,const int*B){
    int par[16]; for(int i=0;i<n;i++)par[i]=i;
    #define F(x) ({int _x=(x); while(par[_x]!=_x) _x=par[_x]=par[par[_x]]; _x;})
    for(int q=0;q<e;q++){ int a=A[2*q],b=A[2*q+1]; int ra=F(a),rb=F(b); if(ra!=rb)par[ra]=rb;
        a=B[2*q]; b=B[2*q+1]; ra=F(a); rb=F(b); if(ra!=rb)par[ra]=rb; }
    int c=0; for(int i=0;i<n;i++) if(F(i)==i) c++;
    return c==1;
}
int main(int argc,char**argv){
    n=atoi(argv[1]); int TRIALS=atoi(argv[2]);
    NS=1<<n; W=(NS+63)/64; e=n/2;
    int A[32],B[32],fix[1<<14]; int nf=0;
    uint64_t bm[(1<<14)/64+2];
    int best=1<<20; int bestA[32],bestB[32];
    int tries=0;
    while(tries<TRIALS){
        randpm(A); randpm(B);
        if(!connected(A,B)) continue;
        tries++;
        nf=0;
        for(int s=0;s<NS;s++){ int ok=1;
            for(int q=0;q<e;q++){ int a=A[2*q],b=A[2*q+1];
                if(((s>>a)&1)==1&&((s>>b)&1)==0){ok=0;break;} }
            if(ok) fix[nf++]=s; }
        memset(bm,0,sizeof(bm)); int c=0;
        for(int t=0;t<nf;t++){ int u=fix[t];
            for(int q=0;q<e;q++){ int a=B[2*q],b=B[2*q+1];
                if(((u>>a)&1)==1&&((u>>b)&1)==0) u=(u&~(1<<a))|(1<<b); }
            if(!((bm[u>>6]>>(u&63))&1)){ bm[u>>6]|=1ULL<<(u&63); c++; } }
        if(c<best){ best=c; memcpy(bestA,A,sizeof A); memcpy(bestB,B,sizeof B); }
    }
    printf("n=%d: sampled rho_%d = %d/%d = %.4f over %d connected random pairs\n",
           n,e,best,nf,(double)best/nf,tries);
    printf("   (2/3)^%d = %.4f\n", e/2, (double)pow(2.0/3.0,e/2));
    printf("   M1="); for(int q=0;q<e;q++) printf("(%d,%d)",bestA[2*q]+1,bestA[2*q+1]+1); printf("\n");
    printf("   M2="); for(int q=0;q<e;q++) printf("(%d,%d)",bestB[2*q]+1,bestB[2*q+1]+1); printf("\n");
    return 0;
}
