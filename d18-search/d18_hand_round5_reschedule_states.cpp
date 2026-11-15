// Enumerate signed restrictions with a normalized retained DAG of height <= 2.
// A repeated comparison is removed when both register tracks last met each
// other. A reversed repeat is represented by swapping fixed output labels.
#include <algorithm>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <vector>
using namespace std;
struct Witness {
    vector<int> initial, labels, depths, repeated;
    vector<vector<int>> gates;
    int real_mask, deep_mask, total;
};
int main(int argc,char**argv) {
    if(argc!=4)return 2;
    ifstream in(argv[1]);int n,d;in>>n>>d;
    int r=stoi(argv[2]),normalize=stoi(argv[3]);
    if(n!=18||(d!=5&&d!=6)||(r!=7&&r!=8))return 3;
    int cap=r==7?4:6;
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
    for(int i=(int)blocks.size()-1;i>=0;--i)remaining[i]=remaining[i+1]+blocks[i].size();
    long long placements=0,accepted=0,repeats_removed=0;
    map<vector<int>,Witness> states;
    auto evaluate=[&](){
        ++placements;
        vector<int> types=initial,labels(n),partner(n,-1),low(n),height(n);
        vector<vector<int>> gates;
        int total=0,removed=0;
        for(int v=0;v<n;++v)labels[v]=types[v]==0?v:-1;
        for(auto &layer:layers)for(auto[a,b]:layer){
            if(types[a]==0&&types[b]==0){
                int x=labels[a],y=labels[b];
                if(normalize&&partner[x]==y&&partner[y]==x){
                    ++removed;
                    if(!low[x])swap(labels[a],labels[b]);
                    continue;
                }
                int h=1+max(height[x],height[y]);
                if(h>2||++total>cap)return;
                height[x]=height[y]=h;partner[x]=y;partner[y]=x;
                low[x]=1;low[y]=0;
                gates.push_back({x,y,h});
            }else if(types[a]>types[b]){
                swap(types[a],types[b]);swap(labels[a],labels[b]);
            }
        }
        ++accepted;repeats_removed+=removed;
        int mask=0,deep=0;vector<int> depths(n,-1),rep;
        for(int v=0;v<n;++v)if(types[v]==0){
            mask|=1<<v;depths[v]=height[labels[v]];
            if(depths[v]==2)deep|=1<<v;
        }
        if(normalize)for(int a=0;a<n;++a)if(types[a]==0)
            for(int b=a+1;b<n;++b)if(types[b]==0){
                int x=labels[a],y=labels[b];
                if(partner[x]==y&&partner[y]==x)rep.push_back(a*n+b);
            }
        vector<int> key={mask,deep,total};key.insert(key.end(),rep.begin(),rep.end());
        states.emplace(key,Witness{initial,labels,depths,rep,gates,mask,deep,total});
    };
    function<void(int,int)> generate=[&](int i,int count){
        if(count>r||count+remaining[i]<r)return;
        if(i==(int)blocks.size()){if(count==r)evaluate();return;}
        auto block=blocks[i];
        if(block.size()==1){
            for(int x=-1;x<=1;++x){initial[block[0]]=x;generate(i+1,count+(x==0));}
        }else for(int x=-1;x<=1;++x)for(int y=x;y<=1;++y){
            initial[block[0]]=x;initial[block[1]]=y;
            generate(i+1,count+(x==0)+(y==0));
        }
    };
    generate(0,0);
    auto vec=[&](const vector<int>&xs){cout<<'[';for(int i=0;i<(int)xs.size();++i){if(i)cout<<',';cout<<xs[i];}cout<<']';};
    cout<<"{\"n\":"<<n<<",\"cut\":"<<d<<",\"reals\":"<<r<<",\"normalize\":"<<normalize
        <<",\"normalized_placements\":"<<placements<<",\"accepted_placements\":"<<accepted
        <<",\"repeats_removed_in_accepted\":"<<repeats_removed<<",\"states\":[";
    bool first=true;
    for(auto &[key,w]:states){
        if(!first)cout<<',';first=false;
        cout<<"{\"real_mask\":"<<w.real_mask<<",\"deep_mask\":"<<w.deep_mask<<",\"total\":"<<w.total;
        cout<<",\"initial\":";vec(w.initial);cout<<",\"labels\":";vec(w.labels);
        cout<<",\"depths\":";vec(w.depths);cout<<",\"repeat_codes\":";vec(w.repeated);
        cout<<",\"gates\":[";for(int i=0;i<(int)w.gates.size();++i){if(i)cout<<',';vec(w.gates[i]);}cout<<"]}";
    }
    cout<<"]}\n";
}
