// Enumerate normalized signed restrictions whose retained prefix consists
// of disjoint two-track components, each compressible to one comparator.
#include <algorithm>
#include <array>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <vector>
using namespace std;
struct Witness {vector<int> initial, final_labels; vector<pair<int,int>> oriented;};
int main(int argc,char**argv) {
    if(argc!=4)return 2;
    ifstream in(argv[1]);int n,d;in>>n>>d;
    int r=stoi(argv[2]),cap=stoi(argv[3]);
    if(n>24||n<2||d<1||r<1||r>n)return 3;
    vector<vector<pair<int,int>>> layers(d);
    vector<vector<int>> mates(d,vector<int>(n));
    for(int t=0;t<d;++t)for(int a=0;a<n;++a)in>>mates[t][a];
    if(!in)return 4;
    for(int t=0;t<d;++t)for(int a=0;a<n;++a){
        int b=mates[t][a];if(b<0)continue;
        if(b>=n||b==a||mates[t][b]!=a)return 5;
        if(a<b)layers[t].push_back({a,b});
    }
    vector<vector<int>> blocks;
    for(auto[a,b]:layers[0])blocks.push_back({a,b});
    for(int a=0;a<n;++a)if(mates[0][a]<0)blocks.push_back({a});
    vector<int> remaining(blocks.size()+1);
    for(int i=(int)blocks.size()-1;i>=0;--i)remaining[i]=remaining[i+1]+blocks[i].size();
    vector<int> initial(n);
    long long placements=0,accepted=0;
    map<int,Witness> states;
    auto evaluate=[&](){
        ++placements;
        vector<int> values=initial,labels(n),partner(n,-1),min_track(n,-1);
        for(int v=0;v<n;++v)labels[v]=values[v]==0?v:-1;
        int edges=0;
        for(auto &layer:layers)for(auto[a,b]:layer){
            if(values[a]==0&&values[b]==0){
                int x=labels[a],y=labels[b];
                if((partner[x]>=0&&partner[x]!=y)||(partner[y]>=0&&partner[y]!=x))return;
                if(partner[x]<0){++edges;if(edges>cap)return;partner[x]=y;partner[y]=x;}
                min_track[min(x,y)]=x;
            } else if(values[a]>values[b]){
                swap(values[a],values[b]);swap(labels[a],labels[b]);
            }
        }
        ++accepted;
        int mask=0;for(int v=0;v<n;++v)if(values[v]==0)mask|=1<<v;
        if(states.count(mask)&&states[mask].oriented.size()<=size_t(edges))return;
        Witness w{initial,labels,{}};
        for(int v=0;v<n;++v)if(partner[v]>v){
            int other=partner[v],lo=min_track[v];w.oriented.push_back({lo,lo==v?other:v});
        }
        states[mask]=w;
    };
    function<void(int,int)> generate=[&](int i,int count){
        if(count>r||count+remaining[i]<r)return;
        if(i==(int)blocks.size()){if(count==r)evaluate();return;}
        auto block=blocks[i];
        if(block.size()==1){
            for(int x=-1;x<=1;++x){initial[block[0]]=x;generate(i+1,count+(x==0));}
        }else{
            for(int x=-1;x<=1;++x)for(int y=x;y<=1;++y){
                initial[block[0]]=x;initial[block[1]]=y;
                generate(i+1,count+(x==0)+(y==0));
            }
        }
    };
    generate(0,0);
    auto vec=[&](const vector<int>&xs){cout<<'[';for(int i=0;i<(int)xs.size();++i){if(i)cout<<',';cout<<xs[i];}cout<<']';};
    cout<<"{\"n\":"<<n<<",\"cut\":"<<d<<",\"reals\":"<<r<<",\"cap\":"<<cap
        <<",\"normalized_placements\":"<<placements<<",\"accepted_placements\":"<<accepted<<",\"states\":[";
    bool first=true;
    for(auto &[mask,w]:states){
        if(!first)cout<<',';first=false;
        cout<<"{\"real_mask\":"<<mask<<",\"initial\":";vec(w.initial);
        cout<<",\"final_labels\":";vec(w.final_labels);
        cout<<",\"compressed_oriented_pairs\":[";
        for(int i=0;i<(int)w.oriented.size();++i){if(i)cout<<',';auto[a,b]=w.oriented[i];cout<<'['<<a<<','<<b<<']';}
        cout<<"]}";
    }
    cout<<"]}\n";
}
