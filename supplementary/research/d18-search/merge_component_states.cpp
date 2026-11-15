// Find nine-real restrictions whose retained interaction components pack
// into forbidden merger blocks: '432', 'both' (432 or333), or 'max4'
// (also441, hence every interaction component has size at most four).
// No SAT; witnesses are checked independently.
#include <algorithm>
#include <array>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <vector>
using namespace std;
struct Witness { vector<int> initial,final_labels; vector<vector<int>> components; };
int main(int argc,char**argv){
    if(argc<2||argc>4)return 2;
    bool both=argc>=3&&string(argv[2])=="both";
    bool max4=argc>=3&&string(argv[2])=="max4";
    bool all=argc>=4&&string(argv[3])=="all";
    ifstream in(argv[1]);int n,d;in>>n>>d;
    if(n<9||n>24||d<1)return 3;
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
    vector<int> remaining(blocks.size()+1),initial(n);
    for(int i=int(blocks.size())-1;i>=0;--i)remaining[i]=remaining[i+1]+blocks[i].size();
    long long placements=0,accepted=0;
    vector<long long> rejected(d);
    map<vector<int>,Witness> witnesses;
    auto evaluate=[&](){
        ++placements;
        vector<int> values=initial,labels(n),parent(n),size(n);
        for(int v=0;v<n;++v){labels[v]=values[v]==0?v:-1;parent[v]=v;size[v]=values[v]==0;}
        auto root=[&](int v){while(parent[v]!=v)v=parent[v];return v;};
        for(int t=0;t<d;++t)for(auto[a,b]:layers[t]){
            if(values[a]==0&&values[b]==0){
                int x=root(labels[a]),y=root(labels[b]);
                if(x!=y){parent[y]=x;size[x]+=size[y];size[y]=0;}
                int fours=0,threes=0;bool bad=false;
                for(int s:size){bad|=s>4;fours+=s==4;threes+=s==3;}
                if(bad||(!max4&&fours>=2)||(!max4&&!both&&threes>=3)){++rejected[t];return;}
            }else if(values[a]>values[b]){
                swap(values[a],values[b]);swap(labels[a],labels[b]);
            }
        }
        ++accepted;
        if(all||witnesses.size()<8){
            map<int,vector<int>> comps;
            for(int v=0;v<n;++v)if(initial[v]==0)comps[root(v)].push_back(v);
            map<int,int> masks;
            for(int v=0;v<n;++v)if(values[v]==0)masks[root(labels[v])]|=1<<v;
            vector<int> key;for(auto&[r,mask]:masks)key.push_back(mask);sort(key.begin(),key.end());
            Witness w{initial,labels,{}};
            for(auto &[key,component]:comps)w.components.push_back(component);
            witnesses.emplace(key,w);
        }
    };
    function<void(int,int)> generate=[&](int i,int real){
        if(real>9||real+remaining[i]<9)return;
        if(i==int(blocks.size())){if(real==9)evaluate();return;}
        auto block=blocks[i];
        if(block.size()==1){
            for(int x=-1;x<=1;++x){initial[block[0]]=x;generate(i+1,real+(x==0));}
        }else{
            for(int x=-1;x<=1;++x)for(int y=x;y<=1;++y){
                initial[block[0]]=x;initial[block[1]]=y;
                generate(i+1,real+(x==0)+(y==0));
            }
        }
    };
    generate(0,0);
    auto vec=[&](const auto&xs){cout<<'[';bool first=true;for(auto x:xs){if(!first)cout<<',';first=false;cout<<x;}cout<<']';};
    cout<<"{\"n\":"<<n<<",\"cut\":"<<d<<",\"reals\":9,\"normalized_placements\":"<<placements
        <<",\"accepted_placements\":"<<accepted<<",\"criterion\":\""<<(max4?"max-component-4":both?"432-or-333":"432")
        <<"\",\"all_unique_states_stored\":"<<(all?"true":"false")<<",\"rejected_by_layer\":";vec(rejected);
    cout<<",\"witnesses\":[";
    bool first=true;
    for(auto&[key,w]:witnesses){
        if(!first)cout<<',';first=false;
        cout<<"{\"cut_component_masks\":";vec(key);cout<<",\"initial\":";vec(w.initial);cout<<",\"final_labels\":";vec(w.final_labels);
        cout<<",\"components\":[";bool f=true;
        for(auto&c:w.components){if(!f)cout<<',';f=false;vec(c);}
        cout<<"]}";
    }
    cout<<"]}\n";
}
