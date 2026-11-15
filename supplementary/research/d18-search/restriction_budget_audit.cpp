// Exhaustively audit every normalized signed placement. No SAT and no sampling
// in the reported extrema or violation counts. Only the exported witness list
// is capped. Usage: audit NETWORK.txt RETAINED_BITMASK SIZE_ONLY WITNESS_LIMIT
// NETWORK.txt begins n d, followed by d rows of n partner indices (-1 = idle).
#include <algorithm>
#include <array>
#include <functional>
#include <fstream>
#include <iostream>
#include <random>
#include <vector>
const int sizes[18]={0,0,1,3,5,9,12,16,19,25,29,35,39,44,48,53,57,63};
const int depths[18]={0,0,1,3,3,5,5,6,6,7,7,8,8,9,9,9,9,10};
struct Stat {
    long long placements=0,violations=0;
    int minimum=10000,active=10000;
    std::array<int,18> witness{};
};
int main(int argc,char**argv) {
    if(argc!=5)return 2;
    std::ifstream in(argv[1]);int n,d;in>>n>>d;
    if(n<3 || n>18 || d<1)return 3;
    std::vector<std::vector<std::pair<int,int>>> net(d);
    std::vector<std::vector<int>> partner(d,std::vector<int>(n));
    for(int t=0;t<d;++t)for(int a=0;a<n;++a)in>>partner[t][a];
    if(!in)return 4;
    for(int t=0;t<d;++t)for(int a=0;a<n;++a) {
        int b=partner[t][a];if(b<0)continue;
        if(b>=n || b==a || partner[t][b]!=a)return 5;
        if(b>a)net[t].emplace_back(a,b);
    }
    if(int(net[0].size())!=n/2)return 6;
    unsigned retained=std::stoul(argv[2]);bool size_only=std::stoi(argv[3]);
    int limit=std::stoi(argv[4]);
    if(retained&~((1u<<18)-4))return 7;
    std::array<Stat,18> stats;
    std::array<int,18> initial{};
    std::vector<std::array<int,18>> bad;
    std::mt19937 rng(20261115);long long bad_seen=0;
    auto evaluate=[&](int r) {
        if(!(retained&(1u<<r)))return;
        auto state=initial;
        int count=0,active=0,first=-1,second=-1;
        for(const auto& layer:net) {
            int row=0;
            for(auto [a,b]:layer) {
                row+=state[a]==0 && state[b]==0;
                if(state[a]>state[b])std::swap(state[a],state[b]);
            }
            count+=row;
            if(row){if(first<0)first=row;else if(second<0)second=row;++active;}
        }
        auto& s=stats[r];++s.placements;
        if(count<s.minimum){s.minimum=count;s.witness=initial;}
        s.active=std::min(s.active,active);
        bool violates=count<sizes[r];
        if(!size_only) {
            violates |= active<depths[r];
            violates |= r==5 && active==5 && first==1 && second==1;
            violates |= r==7 && active==6 && first==1;
            violates |= r==9 && active==7 && std::max(first,second)<=3;
        }
        if(violates) {
            ++s.violations;++bad_seen;
            if(int(bad.size())<limit)bad.push_back(initial);
            else if(limit) {
                long long j=std::uniform_int_distribution<long long>(0,bad_seen-1)(rng);
                if(j<limit)bad[j]=initial;
            }
        }
    };
    auto pairs=net[0];int idle=-1;
    for(int a=0;a<n;++a)if(partner[0][a]<0)idle=a;
    std::function<void(int,int)> generate=[&](int i,int r) {
        int remaining=2*(int(pairs.size())-i)+(idle>=0);
        unsigned possible=0;
        for(int k=r;k<=r+remaining && k<18;++k)possible|=1u<<k;
        if(!(possible&retained))return;
        if(i==int(pairs.size())) {
            if(idle>=0)for(int x=-1;x<=1;++x){initial[idle]=x;evaluate(r+(x==0));}
            else evaluate(r);
            return;
        }
        auto [a,b]=pairs[i];
        for(int x=-1;x<=1;++x)for(int y=x;y<=1;++y) {
            initial[a]=x;initial[b]=y;
            generate(i+1,r+(x==0)+(y==0));
        }
    };
    generate(0,0);
    auto state_json=[&](const std::array<int,18>& a) {
        std::cout<<'[';for(int i=0;i<n;++i){if(i)std::cout<<',';std::cout<<a[i];}std::cout<<']';
    };
    std::cout<<"{\"n\":"<<n<<",\"depth\":"<<d<<",\"size_only\":"<<(size_only?"true":"false")<<",\"results\":[";
    bool comma=false;
    for(int r=2;r<18;++r)if(retained&(1u<<r)) {
        auto&s=stats[r];if(comma)std::cout<<',';comma=true;
        std::cout<<"{\"r\":"<<r<<",\"placements\":"<<s.placements<<",\"violations\":"<<s.violations
                 <<",\"minimum_comparators\":"<<s.minimum<<",\"minimum_active_layers\":"<<s.active<<",\"minimum_witness\":";
        state_json(s.witness);std::cout<<'}';
    }
    std::cout<<"],\"sampled_bad_placements\":[";
    comma=false;for(const auto& s:bad){if(comma)std::cout<<',';comma=true;state_json(s);}
    std::cout<<"]}\n";
}
