/* rho_k = min over pairs of perfect matchings on 2k channels with CONNECTED union
   of |L_M2(Fix(M1))| / |Fix(M1)|.   Exact, exhaustive. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int n,NS,e,nPairs,nLay=0,W;
static int pa[256],pb[256];
static int *lay; static int cur[16],nc;
static int emit(void){ for(int i=0;i<e;i++) lay[(size_t)nLay*e+i]=cur[i]; nLay++; return 0; }
static void gen(int st,int np,int used){ if(np==e){emit();return;}
  for(int i=st;i<nPairs;i++){int a=pa[i],b=pb[i];
    if((used>>a)&1)continue; if((used>>b)&1)continue;
    cur[nc++]=i; gen(i+1,np+1,used|(1<<a)|(1<<b)); nc--;}}
static int P(int l,int t){ return lay[(size_t)l*e+t]; }
static int comps(int l1,int l2){
    int par[16]; for(int i=0;i<n;i++) par[i]=i;
    #define FIND(x) ({int _x=(x); while(par[_x]!=_x) _x=par[_x]=par[par[_x]]; _x;})
    for(int t=0;t<e;t++){ int p1=P(l1,t),p2=P(l2,t);
        int a=pa[p1],b=pb[p1]; int ra=FIND(a),rb=FIND(b); if(ra!=rb) par[ra]=rb;
        a=pa[p2];b=pb[p2]; ra=FIND(a);rb=FIND(b); if(ra!=rb) par[ra]=rb; }
    int c=0; for(int i=0;i<n;i++) if(FIND(i)==i) c++;
    return c;
}
int main(int argc,char**argv){
    n=atoi(argv[1]); NS=1<<n; W=(NS+63)/64; e=n/2; nPairs=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){pa[nPairs]=i;pb[nPairs]=j;nPairs++;}
    /* count then allocate */
    nLay=0; nc=0; { int saveN=0; (void)saveN; }
    { /* count by generating into a temp array of size 0: use a two-pass with a global */
      int *tmp=lay; lay=NULL; 
      /* emit writes lay only if non-null; guard */
      /* simpler: allocate over-generously */
      lay=malloc(40000*e*sizeof(int)); nLay=0; nc=0; gen(0,0,0);
      (void)tmp;
    }
    fprintf(stderr,"n=%d: %d perfect matchings, |Fix|=%d\n",n,nLay,1<<n?0:0);
    uint16_t *act=malloc((size_t)nLay*NS*sizeof(uint16_t));
    for(int l=0;l<nLay;l++){uint16_t*A=act+(size_t)l*NS;
        for(int s=0;s<NS;s++){int v=s;
            for(int t=0;t<e;t++){int pi=P(l,t),a=pa[pi],b=pb[pi];
                if(((v>>a)&1)==1&&((v>>b)&1)==0)v=(v&~(1<<a))|(1<<b);} A[s]=(uint16_t)v;}}
    int nf=3,none;
    { /* |Fix| */
      nf=0; for(int s=0;s<NS;s++){int ok=1;
        for(int t=0;t<e;t++){int pi=P(0,t),a=pa[pi],b=pb[pi];
            if(((s>>a)&1)==1&&((s>>b)&1)==0){ok=0;break;}}
        if(ok)nf++; }
      fprintf(stderr,"   |Fix(M)| = %d\n",nf);
    }
    int *F=malloc(NS*sizeof(int));
    uint64_t *bm=calloc(W,sizeof(uint64_t));
    double best=2.0; int b1=-1,b2=-1, bestcnt=nf+1;
    for(int l1=0;l1<nLay;l1++){
        int k=0;
        for(int s=0;s<NS;s++){int ok=1;
            for(int t=0;t<e;t++){int pi=P(l1,t),a=pa[pi],b=pb[pi];
                if(((s>>a)&1)==1&&((s>>b)&1)==0){ok=0;break;}}
            if(ok)F[k++]=s;}
        for(int l2=0;l2<nLay;l2++){
            if(comps(l1,l2)!=1) continue;
            memset(bm,0,W*sizeof(uint64_t)); int c=0; uint16_t*A=act+(size_t)l2*NS;
            for(int t=0;t<k;t++){int u=A[F[t]];
                if(!((bm[u>>6]>>(u&63))&1)){bm[u>>6]|=1ULL<<(u&63);c++;}}
            if(c<bestcnt){bestcnt=c;b1=l1;b2=l2;}
        }
    }
    printf("n=%d: rho_%d = %d/%d = %.6f\n",n,e,bestcnt,nf,(double)bestcnt/nf);
    printf("   pattern M1 ="); for(int t=0;t<e;t++){int pi=P(b1,t);printf(" (%d,%d)",pa[pi]+1,pb[pi]+1);} printf("\n");
    printf("   pattern M2 ="); for(int t=0;t<e;t++){int pi=P(b2,t);printf(" (%d,%d)",pa[pi]+1,pb[pi]+1);} printf("\n");
    return 0;
}
