// Small local search for counterexamples to proposed restriction-budget lemmas.
// This does not search for or certify sorting networks. The Python driver uses
// an exact symbolic adversary to check every signed placement for each r.
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <random>
#include <vector>
using Net = std::array<std::array<int,18>,10>;
struct Sample { int r; std::array<int,18> state; };
const int sizes[18]={0,0,1,3,5,9,12,16,19,25,29,35,39,44,48,53,57,63};
const int depths[18]={0,0,1,3,3,5,5,6,6,7,7,8,8,9,9,9,9,10};

int energy(const Net& net, const std::vector<Sample>& samples, bool size_only) {
    int e=0;
    for (const auto& sample:samples) {
        auto state=sample.state;
        int count=0,active=0,first=-1,second=-1;
        for (int t=0;t<10;++t) {
            int row=0;
            for (int a=0;a<18;++a) {
                int b=net[t][a]; if(b<=a)continue;
                row += state[a]==0 && state[b]==0;
                if(state[a]>state[b])std::swap(state[a],state[b]);
            }
            count+=row;
            if(row) { if(first<0)first=row; else if(second<0)second=row; ++active; }
        }
        int missing=std::max(0,sizes[sample.r]-count);
        e+=4*missing*missing;
        if(!size_only) {
            missing=std::max(0,depths[sample.r]-active);
            e+=9*missing*missing;
            if(sample.r==5 && active==5 && first==1 && second==1)e+=9;
            if(sample.r==7 && active==6 && first==1)e+=9;
            if(sample.r==9 && active==7 && std::max(first,second)<=3)e+=9;
        }
    }
    return e;
}

bool valid(const Net& net,int t) {
    for(int a=0;a<18;++a) {
        int b=net[t][a];if(b<0)continue;
        if(b==a || b>=18 || net[t][b]!=a)return false;
        if(t>0 && net[t-1][a]==b)return false;
        if(t<9 && net[t+1][a]==b)return false;
        if(t==8 && a<b) {
            if(b-a>3)return false;
            if(b-a==3 && (net[9][a]!=a+1 || net[9][a+2]!=a+3))return false;
            if(b-a==2 && net[9][a]!=a+1 && net[9][a+1]!=a+2)return false;
        }
    }
    return true;
}

int main(int argc,char**argv) {
    if(argc!=6)return 2;
    std::ifstream in(argv[1]);
    Net net;
    for(auto& layer:net)for(int& p:layer)in>>p;
    int ns;in>>ns;
    std::vector<Sample> samples(ns);
    for(auto& s:samples){in>>s.r;for(int&x:s.state)in>>x;}
    if(!in)return 3;
    double seconds=std::stod(argv[3]);
    std::mt19937 rng(std::stoul(argv[4]));
    bool size_only=std::stoi(argv[5]);
    auto begin=std::chrono::steady_clock::now();
    int current=energy(net,samples,size_only), best=current;
    Net best_net=net;
    long iterations=0;
    while(best>0) {
        double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
        if(elapsed>=seconds)break;
        int t=2+rng()%7, a=rng()%18,b=rng()%18;
        if(a==b)continue;
        auto old=net[t];
        int pa=net[t][a],pb=net[t][b];
        if(pa==b) { net[t][a]=net[t][b]=-1; }
        else {
            if(pa>=0)net[t][pa]=-1;
            if(pb>=0)net[t][pb]=-1;
            net[t][a]=b;net[t][b]=a;
            if(pa>=0 && pb>=0 && rng()%8!=0) {net[t][pa]=pb;net[t][pb]=pa;}
        }
        if(!valid(net,t)){net[t]=old;continue;}
        int next=energy(net,samples,size_only);
        double cycle=std::fmod(elapsed,0.2)/0.2;
        double temp=0.3+6.0*(1.0-cycle);
        double u=std::generate_canonical<double,32>(rng);
        if(next<=current || u<std::exp((current-next)/temp)) {
            current=next;
            if(current<best){best=current;best_net=net;}
        } else net[t]=old;
        ++iterations;
    }
    std::ofstream out(argv[2]);
    for(auto& layer:best_net){for(int p:layer)out<<p<<' ';out<<'\n';}
    std::cout<<"{\"energy\":"<<best<<",\"iterations\":"<<iterations<<"}\n";
}
