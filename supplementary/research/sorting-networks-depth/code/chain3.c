/* Sampled greedy descent for larger n: minimise |L_M(F)| over K random maximal layers. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int n,NS,e,K,W;
static uint32_t seed=12345;
static uint32_t rnd(void){ seed=seed*1664525u+1013904223u; return seed; }
static int *F,*tmp,*bestF; static int nF;
static uint64_t *bm;
static int apply_img(const int*L,int aF,int*Out){
    memset(bm,0,W*sizeof(uint64_t)); int c=0;
    for(int t=0;t<aF;t++){ int u=F[t];
        for(int q=0;q<e;q++){ int a=L[2*q],b=L[2*q+1];
            if(((u>>a)&1)==1&&((u>>b)&1)==0) u=(u&~(1<<a))|(1<<b); }
        if(!((bm[u>>6]>>(u&63))&1)){ bm[u>>6]|=1ULL<<(u&63); Out[c++]=u; } }
    return c;
}
static void rand_layer(int*L){
    int ch[32],m=n; for(int i=0;i<n;i++) ch[i]=i;
    if(n%2){ int z=rnd()%n; ch[z]=ch[--m]; }
    for(int i=m-1;i>0;i--){ int j=rnd()%(i+1); int t=ch[i];ch[i]=ch[j];ch[j]=t; }
    for(int q=0;q<e;q++){ int a=ch[2*q],b=ch[2*q+1]; if(a>b){int t=a;a=b;b=t;} L[2*q]=a;L[2*q+1]=b; }
}
int main(int argc,char**argv){
    n=atoi(argv[1]); int T=atoi(argv[2]); K=atoi(argv[3]);
    NS=1<<n; W=(NS+63)/64; e=n/2;
    F=malloc(NS*sizeof(int)); tmp=malloc(NS*sizeof(int)); bestF=malloc(NS*sizeof(int));
    bm=calloc(W,sizeof(uint64_t));
    nF=0; for(int s=0;s<NS;s++){ int ok=1;
        for(int q=0;q<e;q++){ int a=2*q,b=2*q+1;
            if(((s>>a)&1)==1&&((s>>b)&1)==0){ok=0;break;} }
        if(ok) F[nF++]=s; }
    printf("n=%d: |F_1| = %d\n",n,nF); fflush(stdout);
    int prev=nF; int L[64];
    for(int step=2;step<=T;step++){
        int best=nF+100000, bn=0;
        for(int trial=0;trial<K;trial++){
            if(trial==0){ for(int q=0;q<e;q++){ L[2*q]=2*q; L[2*q+1]=2*q+1; } }
            else if(trial==1){ int q=0; for(int i=1;i+1<n&&q<e;i+=2){ L[2*q]=i;L[2*q+1]=i+1;q++; } while(q<e){ rand_layer(L); break; } }
            else rand_layer(L);
            int c=apply_img(L,nF,tmp);
            if(c<best){ best=c; bn=c; memcpy(bestF,tmp,sizeof(int)*c); }
            if(best<=n+2) break;
        }
        memcpy(F,bestF,sizeof(int)*bn); nF=bn;
        printf("  |F_%d| = %d (ratio %.4f)\n",step,nF,(double)nF/prev); fflush(stdout);
        if(nF==prev && step>3) { printf("  (stable)\n"); }
        prev=nF;
    }
    return 0;
}
