#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <vector>
using namespace std;
// Direct finite reduction: N is safely filled, so it must pair two
// sentinels in each transported triple not already peaking in M.
const array<int,12> signs={0,0,1,-1,-1,1,1,1,-1,1,-1,1};
const array<array<int,2>,4> a_pairs={{{3,4},{4,5},{5,6},{2,4}}};
const array<int,5> b_vertices={8,10,11,9,7};
vector<array<int,12>> make_states() {
    vector<array<int,12>> result;
    for(auto ab:a_pairs) for(int b:b_vertices) {
        array<int,12> state{};
        for(int v:{ab[0],ab[1],b}) state[v]=signs[v];
        result.push_back(state);
    }
    return result;
}
const auto states=make_states();
vector<pair<int,int>> matching;
uint64_t matchings_count=0, search_nodes=0;
map<int,int> by_size,core_sizes,cross_counts;
int four_replacements=0, five_without_four=0;
struct CoreRecord {int count=0; vector<pair<int,int>> representative;};
map<vector<int>,CoreRecord> cores;

bool hit(const vector<int>& triples, uint32_t remaining, int used) {
    ++search_nodes;
    if(!remaining) return true;
    vector<int> best;
    int best_count=4;
    for(int k=0;k<(int)triples.size();++k) if(remaining&(1u<<k)) {
        vector<int> candidates;
        int available=triples[k]&~used;
        for(int i=0;i<12;++i) if(available&(1<<i))
            for(int j=i+1;j<12;++j) if(available&(1<<j))
                candidates.push_back((1<<i)|(1<<j));
        if(candidates.empty()) return false;
        if((int)candidates.size()<best_count) {
            best_count=candidates.size(); best=candidates;
            if(best_count==1) break;
        }
    }
    for(int edge:best) {
        uint32_t next=remaining;
        for(int k=0;k<(int)triples.size();++k)
            if((triples[k]&edge)==edge) next &= ~(1u<<k);
        if(hit(triples,next,used|edge)) return true;
    }
    return false;
}
bool hit(const vector<int>& triples) {
    return hit(triples,(1u<<triples.size())-1,0);
}

void inspect() {
    ++matchings_count; ++by_size[matching.size()];
    vector<int> triples;
    int cross=0;
    for(auto [i,j]:matching) if(i>=2&&i<=6&&j>=7) ++cross;
    ++cross_counts[cross];
    for(auto state:states) {
        int rr=0;
        for(auto [i,j]:matching) {
            rr += state[i]==0 && state[j]==0;
            if(state[i]>state[j]) swap(state[i],state[j]);
        }
        if(rr>=4) continue;
        int mask=0;
        for(int i=0;i<12;++i) if(state[i]) mask |= 1<<i;
        if(__builtin_popcount((unsigned)mask)!=3) abort();
        triples.push_back(mask);
    }
    sort(triples.begin(),triples.end());
    triples.erase(unique(triples.begin(),triples.end()),triples.end());
    if(hit(triples)) {
        cerr<<"COUNTEREXAMPLE first matching";
        for(auto [a,b]:matching) cerr<<" "<<a<<","<<b;
        cerr<<"\n"; exit(1);
    }
    const auto full_triangles=triples;
    // Monotonicity makes one deletion pass inclusion-minimal.
    for(int i=(int)triples.size()-1;i>=0;--i) {
        auto candidate=triples; candidate.erase(candidate.begin()+i);
        if(!hit(candidate)) triples=std::move(candidate);
    }
    if(triples.size()>4) {
        bool found=false;
        int n=full_triangles.size();
        for(int a=0;a<n&&!found;++a) for(int b=a+1;b<n&&!found;++b)
            for(int c=b+1;c<n&&!found;++c) for(int d=c+1;d<n&&!found;++d) {
                vector<int> candidate={full_triangles[a],full_triangles[b],full_triangles[c],full_triangles[d]};
                if(!hit(candidate)) {triples=std::move(candidate);found=true;}
            }
        if(found) ++four_replacements; else ++five_without_four;
    }
    ++core_sizes[triples.size()];
    auto &record=cores[triples];
    if(record.count++==0) record.representative=matching;
}
void enumerate(int remaining) {
    if(!remaining) {inspect();return;}
    int a=__builtin_ctz((unsigned)remaining);
    remaining &= ~(1<<a);
    enumerate(remaining);
    for(int b=a+1;b<12;++b) if(remaining&(1<<b)) {
        matching.push_back({a,b});
        enumerate(remaining&~(1<<b));
        matching.pop_back();
    }
}
void print_map(ostream& out,const map<int,int>& values) {
    out<<"{"; bool first=true;
    for(auto [a,b]:values) {if(!first)out<<",";first=false;out<<"\""<<a<<"\":"<<b;}
    out<<"}";
}
int main(int argc,char**argv) {
    if(argc!=2) {cerr<<"Usage: d12_triangle_scan OUTPUT_PREFIX\n";return 2;}
    auto start=chrono::steady_clock::now();
    enumerate((1<<12)-1);
    ofstream data(string(argv[1])+"-cores.jsonl");
    for(auto &[triangles,r]:cores) {
        data<<"{\"count\":"<<r.count<<",\"first_matching\":[";
        for(int i=0;i<(int)r.representative.size();++i) {
            if(i)data<<",";auto[a,b]=r.representative[i];data<<"["<<a<<","<<b<<"]";
        }
        data<<"],\"triangles\":[";
        for(int i=0;i<(int)triangles.size();++i) {
            if(i)data<<",";data<<"[";bool first=true;
            for(int v=0;v<12;++v) if(triangles[i]&(1<<v)) {if(!first)data<<",";first=false;data<<v;}
            data<<"]";
        }
        data<<"]}\n";
    }
    double elapsed=chrono::duration<double>(chrono::steady_clock::now()-start).count();
    ostringstream report;
    report<<"{\"status\":\"VERIFIED\",\"matchings\":"<<matchings_count
        <<",\"distinct_labelled_cores\":"<<cores.size()<<",\"search_nodes\":"<<search_nodes
        <<",\"seconds\":"<<elapsed<<",\"by_size\":";print_map(report,by_size);
    report<<",\"by_cross_edges\":";print_map(report,cross_counts);
    report<<",\"deletion_minimal_core_sizes\":";print_map(report,core_sizes);
    report<<",\"five_cores_replaced_by_four\":"<<four_replacements
        <<",\"five_cores_with_no_four_subfamily\":"<<five_without_four
        <<",\"sat_used\":false,\"minimality\":\"inclusion minimal; tested every four-subfamily when initial core size exceeds four\",\"signed_states\":[";
    for(int i=0;i<(int)states.size();++i) {
        if(i)report<<",";report<<"[";
        for(int v=0;v<12;++v) {if(v)report<<",";report<<states[i][v];}
        report<<"]";
    }
    report<<"]}\n";
    ofstream summary(string(argv[1])+"-summary.json");summary<<report.str();
    cout<<report.str();
}
