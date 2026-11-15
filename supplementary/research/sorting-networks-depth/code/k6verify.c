/* Rigorous: is there ANY pair of perfect matchings on 12 channels with
   |L_M2(Fix(M1))| < 216 ?   (216 = 729 * 8/27, the packing bound for e=6)
   Early exit once the count reaches 216 -> only "failures" are fully counted. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int n,NS,e,nLay;
static int *lay; static int cur[16],nc;
static int pa[256],pb[256],nPairs;
static void emit(void){ for(int i=0;i<e;i++) lay[(size_t)nLay*e+i]=cur[i]; nLay++; }
static void gen(int st,int np,int used){ if(np==e){emit();return;}
  for(int i=st;i<nPairs;i++){int a=pa[i],b=pb[i];
    if((used>>a)&1)continue; if((used>>b)&1)continue;
    cur[nc++]=i; gen(i+1,np+1, used|(1<<a)|(1<<b)); nc--;}}
static int P(int l,int t){ return lay[(size_t)l*e+t]; }
int main(int argc,char**argv){
    n=atoi(argv[1]); e=n/2; NS=1<<n;
    nPairs=0; for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){pa[nPairs]=i;pb[nPairs]=j;nPairs++;}
    lay=malloc(40000*e*sizeof(int)); nLay=0; nc=0; gen(0,0,0);
    fprintf(stderr,"n=%d: %d perfect matchings\n",n,nLay);
    int LIMIT=atoi(argv[2]);
    int *fix=malloc(NS*sizeof(int));
    uint64_t bm[(1<<14)/64];

    int worst=LIMIT; long fails=0;
    for(int l1=0;l1<nLay;l1++){
        int nf=0;
        for(int s=0;s<NS;s++){ int ok=1;
            for(int t=0;t<e;t++){ int pi=P(l1,t),a=pa[pi],b=pb[pi];
                if(((s>>a)&1)==1&&((s>>b)&1)==0){ok=0;break;} }
            if(ok) fix[nf++]=s; }
        for(int l2=0;l2<nLay;l2++){
            memset(bm,0,(NS+63)/64*sizeof(uint64_t));
            int c=0, over=0;
            for(int t=0;t<nf;t++){ int u=fix[t];
                for(int q=0;q<e;q++){ int pi=P(l2,q),a=pa[pi],b=pb[pi];
                    if(((u>>a)&1)==1&&((u>>b)&1)==0) u=(u&~(1<<a))|(1<<b); }
                if(!((bm[u>>6]>>(u&63))&1)){ bm[u>>6]|=1ULL<<(u&63); c++;
                    if(c>=LIMIT){ over=1; break; } } }
            if(!over){ fails++;
                printf("  COUNTEREXAMPLE: |image| = %d < %d   M1=",c,LIMIT);
                for(int t=0;t<e;t++){int pi=P(l1,t);printf("(%d,%d)",pa[pi]+1,pb[pi]+1);}
                printf("  M2=");
                for(int t=0;t<e;t++){int pi=P(l2,t);printf("(%d,%d)",pa[pi]+1,pb[pi]+1);}
                printf("\n"); fflush(stdout);
                if(fails>5) return 1;
            }
        }
        if(l1%1000==0) fprintf(stderr,"  ... M1 %d/%d, failures so far %ld\n",l1,nLay,fails);
    }
    printf("n=%d: pairs with |image| < %d : %ld  (0 means the inequality holds)\n",n,LIMIT,fails);
    return fails?1:0;
}
