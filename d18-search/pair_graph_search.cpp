// Bounded counterexample search for the degree/parity obstruction conjecture.
// Input: eight rows of 18 matching partners. Optional final argument gives
// the number of fixed initial layers (default two).
// Output: the best prefix and exact pair graph; this is NOT a lower-bound proof.
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <map>
#include <random>
#include <vector>
using Layer=std::array<int,18>;
using Net=std::array<Layer,8>;
struct Score {int energy,excess,odd,edge_count,cubes,output_count,profile_excess;std::array<unsigned,18> adjacency{};};
std::string criterion="graph";
bool escapes(const Score& s) {return criterion=="profile"?s.profile_excess==0:criterion=="outputs"?s.output_count<60:criterion=="cube"?s.cubes==0:s.excess==0 && s.odd==0 && (criterion!="all" || s.cubes==0);}
std::array<unsigned,1<<18> seen{};unsigned stamp=0;

std::vector<unsigned> propagate_layer(const std::vector<unsigned>& inputs,const Layer& layer) {
    std::vector<std::pair<unsigned,unsigned>> edges;
    for(int a=0;a<18;++a)if(layer[a]>a)edges.emplace_back(1u<<a,1u<<layer[a]);
    ++stamp;std::vector<unsigned> out;out.reserve(inputs.size());
    for(unsigned x:inputs) {
        for(auto [a,b]:edges)if((x&a) && !(x&b))x^=a|b;
        if(seen[x]!=stamp){seen[x]=stamp;out.push_back(x);}
    }
    return out;
}

Score score(const std::vector<unsigned>& values) {
    ++stamp;for(unsigned x:values)seen[x]=stamp;
    Score out{};
    out.output_count=values.size();
    std::array<int,19> counts{};
    for(unsigned x:values)++counts[18-__builtin_popcount(x)];
    for(int begin=0;begin<18;) {
        int end=begin+1;while(counts[end]!=1)++end;
        int n=end-begin,best=100000;
        for(int shift=0;shift<2;++shift) {
            std::vector<std::pair<int,int>> blocks;
            for(int i=0;i<n;) {
                if(i>=shift && (i-shift)%2==0 && i+1<n){blocks.emplace_back(i,i+1);i+=2;}
                else {blocks.emplace_back(i,i);++i;}
            }
            std::vector<int> capacity(n+1,1);
            for(unsigned i=0;i<blocks.size();++i) {
                auto [a,b]=blocks[i];
                if(a!=b)capacity[a+1]=blocks.size()==1?2:(i==0 || i+1==blocks.size()?3:5);
                if(i+1<blocks.size())capacity[b+1]=2;
            }
            int penalty=0;for(int i=0;i<=n;++i)penalty+=std::max(0,counts[begin+i]-capacity[i]);
            best=std::min(best,penalty);
        }
        if(n==4) {
            int penalty=0;for(int i=1;i<4;++i)penalty+=std::max(0,counts[begin+i]-4);
            best=std::min(best,penalty);
        }
        out.profile_excess+=best;begin=end;
    }
    for(unsigned x:values) {
        std::vector<unsigned> axes;
        for(int a=0;a<18;++a)if(!(x>>a&1) && seen[x|(1u<<a)]==stamp)axes.push_back(1u<<a);
        for(unsigned a=0;a<axes.size();++a)for(unsigned b=a+1;b<axes.size();++b)
            if(seen[x|axes[a]|axes[b]]==stamp)
                for(unsigned c=b+1;c<axes.size();++c)
                    if(seen[x|axes[a]|axes[c]]==stamp && seen[x|axes[b]|axes[c]]==stamp
                        && seen[x|axes[a]|axes[b]|axes[c]]==stamp)++out.cubes;
    }
    for(unsigned x:values)for(int a=0;a<18;++a)if(x>>a&1)
        for(int b=a+1;b<18;++b)if(!(x>>b&1) && seen[x^(1u<<a)^(1u<<b)]==stamp) {
            out.adjacency[a]|=1u<<b;out.adjacency[b]|=1u<<a;
        }
    std::vector<unsigned> six_sets;
    for(int a=0;a<18;++a) {
        int degree=__builtin_popcount(out.adjacency[a]);out.edge_count+=degree;
        out.excess+=std::max(0,degree-5)*std::max(0,degree-5);
        if(degree==5)six_sets.push_back(out.adjacency[a]|(1u<<a));
    }
    out.edge_count/=2;
    std::map<unsigned,int> cells;
    for(int a=0;a<18;++a) {
        unsigned signature=0;
        for(unsigned i=0;i<six_sets.size();++i)if(six_sets[i]>>a&1)signature|=1u<<i;
        ++cells[signature];
    }
    for(auto [signature,count]:cells)if(signature && count%2)out.odd+=count;
    out.energy=(criterion=="cube"?10000*out.cubes:10000*out.excess+100*out.odd+(criterion=="all"?1000*out.cubes:0))
        +2*out.edge_count+int(values.size());
    if(criterion=="outputs")out.energy=out.output_count;
    if(criterion=="profile")out.energy=100*out.profile_excess+out.output_count;
    return out;
}

bool valid(const Net& net,int t) {
    for(int a=0;a<18;++a) {
        int b=net[t][a];if(b<0)continue;
        if(b==a || b>=18 || net[t][b]!=a)return false;
        if(t>0 && net[t-1][a]==b)return false;
        if(t<7 && net[t+1][a]==b)return false;
    }
    return true;
}

void save(const char* path,const Net& net,const std::vector<unsigned>& values,Score s,long iterations,double seconds) {
    std::ofstream out(path);
    out<<"{\"n\":18,\"prefix_depth\":8,\"criterion\":\""<<criterion<<"\",\"status\":\""<<(escapes(s)?"ESCAPES_TARGET_TESTS":"OBSTRUCTED")
       <<"\",\"iterations\":"<<iterations<<",\"seconds\":"<<seconds<<",\"degree_excess\":"<<s.excess
       <<",\"odd_cell_vertices\":"<<s.odd<<",\"cubes3\":"<<s.cubes<<",\"profile_excess\":"<<s.profile_excess<<",\"outputs\":"<<values.size()<<",\"pair_edges\":"<<s.edge_count<<",\"degree\":[";
    for(int a=0;a<18;++a){if(a)out<<',';out<<__builtin_popcount(s.adjacency[a]);}
    out<<"],\"layers\":[";
    for(int t=0;t<8;++t) {
        if(t)out<<',';out<<'[';bool comma=false;
        for(int a=0;a<18;++a)if(net[t][a]>a){if(comma)out<<',';comma=true;out<<'['<<a<<','<<net[t][a]<<']';}
        out<<']';
    }
    out<<"]}\n";
}

int main(int argc,char**argv) {
    if(argc<5 || argc>7)return 2;
    std::ifstream in(argv[1]);Net net;
    for(auto& layer:net)for(int& p:layer)in>>p;if(!in)return 3;
    double limit=std::stod(argv[3]);std::mt19937 rng(std::stoul(argv[4]));
    int fixed=argc>=6?std::stoi(argv[5]):2;
    if(argc==7)criterion=argv[6];
    if(criterion!="graph" && criterion!="cube" && criterion!="all" && criterion!="outputs" && criterion!="profile")return 5;
    if(fixed<1 || fixed>=8)return 4;
    std::array<std::vector<unsigned>,9> cache;
    cache[0].resize(1<<18);for(unsigned x=0;x<cache[0].size();++x)cache[0][x]=x;
    for(int t=0;t<8;++t)cache[t+1]=propagate_layer(cache[t],net[t]);
    auto current=score(cache[8]),best=current;auto best_net=net;auto best_values=cache[8];
    auto begin=std::chrono::steady_clock::now();long iterations=0;double elapsed=0;
    while(elapsed<limit && !escapes(best)) {
        elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
        int t=fixed+rng()%(8-fixed),a=rng()%18,b=rng()%18;if(a==b)continue;
        auto old=net[t];int pa=net[t][a],pb=net[t][b];
        if(pa==b)net[t][a]=net[t][b]=-1;
        else {
            if(pa>=0)net[t][pa]=-1;if(pb>=0)net[t][pb]=-1;
            net[t][a]=b;net[t][b]=a;
            if(pa>=0 && pb>=0 && rng()%8){net[t][pa]=pb;net[t][pb]=pa;}
        }
        if(!valid(net,t)){net[t]=old;continue;}
        std::array<std::vector<unsigned>,9> candidate;
        for(int k=t;k<8;++k)candidate[k+1]=propagate_layer(k==t?cache[t]:candidate[k],net[k]);
        auto next=score(candidate[8]);
        double cycle=std::fmod(elapsed,0.5)/0.5;
        double temperature=2+2500*(1-cycle);
        if(criterion=="outputs")temperature=0.02+2.0*(1-cycle);
        if(criterion=="profile")temperature=1+40*(1-cycle);
        if(escapes(next) || next.energy<=current.energy || std::generate_canonical<double,32>(rng)<std::exp((current.energy-next.energy)/temperature)) {
            current=next;
            for(int k=t+1;k<=8;++k)cache[k]=std::move(candidate[k]);
            if(current.energy<best.energy || escapes(current))
                {best=current;best_net=net;best_values=cache[8];}
        } else net[t]=old;
        ++iterations;
    }
    save(argv[2],best_net,best_values,best,iterations,elapsed);
    std::cout<<"iterations="<<iterations<<" outputs="<<best_values.size()<<" degree_excess="<<best.excess<<" odd_cell_vertices="<<best.odd<<" cubes3="<<best.cubes<<" seconds="<<elapsed<<'\n';
}
