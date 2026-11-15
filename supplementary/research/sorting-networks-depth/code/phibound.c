/* Phi(M*,M) = max over u in Fix(M) of #{v in Fix(M*) : L_M(v)=u}
   = the largest fiber; gives |L_M(F)| >= |F|/Phi for every F subset of Fix(M*).
   Also reports the ACHIEVED average |Fix(M*)| / |L_M(Fix(M*))| for comparison. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int n,NS,e,W;
static int pa[512],pb[512],nPairs;
static int *lay,*L1idx;
static int nLay;
static int cur[16],nc;
static int counting=1;
static void emit(void){ if(!counting) for(int i=0;i<e;i++) lay[(size_t)nLay*e+i]=cur[i]; nLay++; }
static void gen(int st,int np,int used){ if(np==e){emit();return;}
  for(int i=st;i<nPairs;i++){int a=pa[i],b=pb[i];
    if((used>>a)&1)continue; if((used>>b)&1)continue;
    cur[nc++]=i; gen(i+1,np+1,used|(1<<a)|(1<<b)); nc--;}}
static int P(int l,int t){ return lay[(size_t)l*e+t]; }
static int inFix(int v,int l){ for(int t=0;t<e;t++){int pi=P(l,t),a=pa[pi],b=pb[pi];
    if(((v>>a)&1)==1&&((v>>b)&1)==0) return 0;} return 1; }
int main(int argc,char**argv){
    n=atoi(argv[1]);
    NS=1<<n; W=(NS+63)/64; nPairs=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){pa[nPairs]=i;pb[nPairs]=j;nPairs++;}
    e=n/2; counting=1;nLay=0;nc=0;gen(0,0,0);
    lay=malloc((size_t)nLay*e*sizeof(int)); counting=0;nLay=0;nc=0;gen(0,0,0);
    /* the brick chain layers given on the command line as "a,b,c,d,..." pairs are hard to pass;
       instead: M* = layer index 0 = adjacent pairs (2q,2q+1); M = shifted adjacent */
    int *Ms=malloc(e*sizeof(int)), *Mm=malloc(e*sizeof(int));
    for(int q=0;q<e;q++){ Ms[q]=q*((n)); } /* placeholder */
    /* adjacent pairs (0,1),(2,3),... encoded as pair index */
    int idx=0;
    for(int q=0;q<e;q++){ int a=2*q,b=2*q+1;
        for(int t=0;t<nPairs;t++) if(pa[t]==a&&pb[t]==b){ Ms[q]=t; break; } }
    /* shifted adjacent (1,2),(3,4),... */
    for(int q=0;q<e;q++){ int a=2*q+1,b=2*q+2;
        int found=-1;
        for(int t=0;t<nPairs;t++) if(pa[t]==a&&pb[t]==b){ found=t; break; }
        Mm[q]=found; }
    /* build Fix(Ms) as list */
    int *Fs=malloc(NS*sizeof(int)), *Fm=malloc(NS*sizeof(int));
    int ns=0,nm=0;
    for(int v=0;v<NS;v++){ int ok=1;
        for(int q=0;q<e;q++){ int a=2*q,b=2*q+1; if(((v>>a)&1)==1&&((v>>b)&1)==0){ok=0;break;} }
        if(ok) Fs[ns++]=v; }
    for(int v=0;v<NS;v++){ int ok=1;
        for(int q=0;q<e;q++){ int a=2*q+1,b=2*q+2; if(a<n&&b<n){ if(((v>>a)&1)==1&&((v>>b)&1)==0){ok=0;break;} } }
        if(ok) Fm[nm++]=v; }
    /* fiber sizes for L_M on Fix(M*) */
    int *cnt=calloc(NS,sizeof(int)), *img=malloc(NS*sizeof(int));
    for(int t=0;t<ns;t++){ int v=Fs[t], u=v;
        for(int q=0;q<e;q++){ int a=2*q+1,b=2*q+2;
            if(b<n && ((u>>a)&1)==1 && ((u>>b)&1)==0) u=(u&~(1<<a))|(1<<b); }
        cnt[u]++; }
    int maxfib=0, distinct=0;
    for(int u=0;u<NS;u++) if(cnt[u]){ distinct++; if(cnt[u]>maxfib) maxfib=cnt[u]; }
    printf("n=%d  M* = adjacent, M = shifted adjacent\n",n);
    printf("  |Fix(M*)| = %d,  |L_M(Fix(M*))| = %d,  achieved average fiber = %.3f\n",
           ns,distinct,(double)ns/distinct);
    printf("  max fiber (Phi) = %d   => provable bound |L_M(F)| >= |F|/%d for every F subset Fix(M*)\n",
           maxfib,maxfib);
    return 0;
}
