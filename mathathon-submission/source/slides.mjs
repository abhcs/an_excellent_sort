// Editable slide source. Every substantive claim maps to report.tex.
// The module works with a viewer-bound presentation or @oai/artifact-tool.
export const slideSize = { width: 1280, height: 720 };
export const fontPolicy = { basis: 'design', families: ['DejaVu Sans'] };
const C = { paper:'#F7F6F1', ink:'#142B3D', muted:'#536573', teal:'#087E8B', amber:'#A65D16', line:'#D7DDD9' };
const FONT = 'DejaVu Sans';
const base = 'https://github.com/abhcs/an_excellent_sort/blob/7bcc462c92af6ea523cf2a79c03070dc4c21b770/';
function text(slide, content, x, y, w, h, size=28, color=C.ink, bold=false) {
  const s=slide.shapes.add({geometry:'textbox',name:content.slice(0,45),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  s.text=content;
  s.text.style={typeface:FONT,fontSize:size,color,bold};
  return s;
}
function table(slide, values, y, widths, rowHeight=70, size=26) {
  const t=slide.tables.add({rows:values.length,columns:values[0].length,left:72,top:y,width:1136,height:rowHeight*values.length,columnWidths:widths,values});
  t.borders.assign({fill:C.line,width:1,style:'solid'});
  t.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({
    fill:C.paper,textStyle:{typeface:FONT,fontSize:size,color:C.ink},margins:{left:16,right:12,top:14,bottom:10}
  });
  t.cells.block({row:0,column:0,rowCount:1,columnCount:values[0].length}).assign({fill:C.ink,textStyle:{typeface:FONT,fontSize:size,color:'#FFFFFF',bold:true}});
  return t;
}
function slide(p,title,section,note,sources=[],tag='') {
  const s=p.slides.add({width:1280,height:720});s.background.fill=C.paper;
  text(s,title,72,54,1136,105,44,C.ink,true);
  if(tag) text(s,tag,72,166,1136,38,21,C.teal,true);
  text(s,`Report ${section}`,72,668,1010,25,16,C.muted);
  text(s,String(p.slides.items.length).padStart(2,'0'),1150,662,58,32,19,C.muted);
  s.speakerNotes.text=`${note}\n\nEvidence: report.tex, ${section}.\nSources:\n${sources.map(f=>f.startsWith('http')?f:base+f).join('\n')}`;
  return s;
}
export function buildSlides(p) {
  let s;
  s=slide(p,'Understanding sorting\nnetwork depth','§1 and §11','0:40. Explain our intent: extracting understandable reasons for depth. Introduce the team and say that this report integrates structural lower bounds and the collaborator construction/AKS snapshot.',['CHECKPOINT.md']);
  text(s,'Constructions, signed restrictions, and current limits',72,275,1100,76,34,C.teal);
  text(s,'An Excellent Sort',72,420,1100,42,30,C.ink,true);
  text(s,'Kevin Shu · University of Waterloo\nHeechang Kim · Seoul National University\nAbhishek Singh · Independent',72,477,1110,113,24,C.muted);
  text(s,'Mathathon 2026   /   Problem 47   /   Computation/Applied Math',72,616,1110,31,20,C.muted);

  s=slide(p,'Our research question','§1 and §8','1:00. Keep background brief. AKS is prior work. The official problem asks for construction or exposition. We have finite constructions, unfinished AKS analysis, and structural lower bounds; no complete simplified asymptotic construction.',['https://competition.sair.foundation/competitions/mathathon/problems/47','https://arxiv.org/abs/1412.5302']);
  text(s,'Can we make shallow sorting networks easier to construct and explain?',72,185,1120,125,42,C.teal,true);
  text(s,'Use SAT to expose constraints and LLMs to help extract structure.\nTurn search certificates into reusable mathematical arguments.',72,350,1120,100,31);
  text(s,'Completed: human-understandable lower bounds through 10 wires.\nNext: structural arguments that reach beyond large case searches.',72,525,1120,100,29,C.amber);



  s=slide(p,'Human proofs through ten wires','§1, §2 and Appendix A','1:15. Emphasize the completed contribution. Our starting point lacked a complete hand derivation. We now obtain every optimal-depth lower bound through ten wires from elementary restrictions, a five-wire thin-layer obstruction, and monotonicity. The upper constructions are known; no SAT or computer-found size minimum is a premise of these lower bounds.',['depth-hand-proofs/README.md']);
  text(s,'A complete human-understandable chain of lower bounds',72,185,1136,90,35,C.teal,true);
  table(s,[['Wires','1','2','3','4','5','6','7','8','9','10'],['D(n)','0','1','3','3','5','5','6','6','7','7']],320,[128,100,100,100,100,100,100,100,100,100,108],74,25);
  text(s,'Signed restrictions + one five-wire obstruction + monotonicity',72,520,1136,64,31);
  text(s,'No SAT result or computer-found comparator-size bound is a premise.\nKnown constructions match every bound.',72,594,1136,64,25,C.muted);

  s=slide(p,'Signed restrictions','§2','1:00. A sentinel is a fixed infinity. Reals are arbitrary and independent. Comparisons against sentinels only route them. Deleting these paths leaves a smaller sorting network, after untangling.',['depth-hand-proofs/README.md','depth-hand-proofs/extension.md']);
  text(s,'Fix selected inputs to −∞ or +∞',72,185,1136,60,36,C.teal,true);
  table(s,[['Comparator inputs','Effect on the real problem'],['Real + sentinel','Predetermined routing'],['Real + real','One retained comparison'],['Two sentinels','No real comparison']],280,[420,716],68,27);
  text(s,'A blind layer has no real-real comparison.\nEvery fixed placement must be compatible with the same suffix.',72,588,1136,66,25);

  s=slide(p,'Two blind layers','§2, Theorem 2.1','1:00. The union of two matching layers is bipartite. Choose one color in each component, avoiding the first-layer idle vertex. Place signs so those sentinels stay put in layer one. The table is a nine-wire example. R means arbitrary real, not the number zero.',['depth-hand-proofs/extension.md']);
  text(s,'D(n) ≥ D(⌈n/2⌉) + 2       for n ≥ 3',72,185,1136,72,42,C.teal,true);
  text(s,'L₁ = 01  23  45  67       L₂ = 02  13  46  57',72,290,1136,52,30);
  table(s,[['Wire','0','1','2','3','4','5','6','7','8'],['Input','−∞','R','R','+∞','−∞','R','R','+∞','R'] ],375,[128,112,112,112,112,112,112,112,112,112],74,27);
  text(s,'Five reals meet only sentinels in both layers.\nThe remaining network must still sort all five.',72,568,1136,86,29);


  s=slide(p,'A search class becomes a nine-row proof','§6.1','1:20. This is the six-cycle H9 class. Explain the invariant: one run has negative infinities, the other positive, with disjoint supports. Joint wire types are totally ordered, so their support disjointness persists. Both real sets have size six and their intersection has size three. A matching cannot pair both. The six-wire profile forces the next two layer forms; nine symbolic rows of four-sentinel placements produce a forbidden five-wire thin profile. All 72 parameter instances were freshly checked.',['depth-hand-proofs/h9-cycle-case.md']);
  text(s,'Two opposite-sign restrictions move through the same suffix',72,190,1136,84,34,C.teal,true);
  text(s,'Their six-real sets always overlap in three wires.\nA matching cannot pair both sets internally.',72,325,1136,108,35);
  text(s,'Odd intersection → forced layer forms → nine explicit rows',72,490,1136,80,32,C.teal,true);
  text(s,'The contradiction is a short hand certificate.\nFresh replay covers its 72 parameter instances; no SAT premise.',72,591,1136,70,26,C.muted);

  s=slide(p,'H9: expanding the human proof','§6.1','0:50. State H9 before explaining the number. It forbids two first layers both capped at three in a depth-seven nine-wire sorter. The transfer theorem then derives D11≥8. Do not turn local hand certificates into a claim of full hand coverage.',['depth-hand-proofs/h9.md','CHECKPOINT.md']);
  text(s,'H9: a depth-seven nine-wire sorter must use four\ncomparators in at least one of its first two layers',72,190,1136,105,33);
  text(s,'26 / 50',72,345,530,115,78,C.teal,true);
  text(s,'classes have hand coverage\nafter the structural follow-up',625,361,580,95,30);
  text(s,'The new (4,3,2)-merger argument completes another hand class.\nThe full H9 lemma still has independent SAT and non-SAT evidence.',72,535,1136,110,27,C.amber);


  s=slide(p,'A reusable component theorem','§6.4','1:10. This comes from hand lower bounds for merging sorted blocks of sizes 4+3+2, 3+3+3 and 4+4+1. If all nine-real components had size at most four, pack them into one of those block shapes. The prefix fixes every input already sorted within the blocks, so four remaining layers would have to perform a forbidden merger. Components need not have been sorted by the prefix.',['d18-search/merge-component-obstruction.md']);
  text(s,'Four layers before the end:',72,190,1136,65,38,C.teal,true);
  text(s,'Every nine-real restriction must have an interaction\ncomponent containing at least five tracks.',72,295,1136,116,36);
  text(s,'Hand merger bounds for 4+3+2, 3+3+3, and 4+4+1\nturn local obstructions into a condition at any ambient width.',72,470,1136,108,30);
  text(s,'It rejects 34 saved D13 witnesses; complete-case counts are unchanged.',72,613,1136,40,24,C.amber);

  s=slide(p,'Current lower-bound evidence','§1, Table 1','1:10. Explain the denominator carefully: complete two-layer representatives, not a proportion of all networks. Published D13 and D17 values are already known. Our objective is more structural explanations.',['CHECKPOINT.md','d18-search/results/structural-cover-progress-round2.json']);
  table(s,[['Target','Checkpoint result','Still missing'],['D(13) ≥ 9','4 / 117 complete cases','113 cases'],['D(17) ≥ 10','3 / 609 complete cases','606 cases'],['D(18) ≥ 11','0 / 411 complete cases','A complete obstruction'] ],190,[290,440,406],86,27);
  text(s,'Eighteen wires: hand exclusions cover selected five- and six-layer\nprefixes. The known depth interval remains 10 ≤ D(18) ≤ 11.',72,568,1136,85,25,C.amber);

  s=slide(p,'Rank positions constrain a common ending','§6.2','1:15. A wire can reach at most four outputs in two layers, and an output has a backward cone of at most four wires. Adjacent binary probes compute the exact rank-position relation. We enforce common realizability across the prefix and, where used, common ending matchings.',['d18-search/certificate-guided-frontier.md','d18-search/d13_feedback_round2.md']);
  text(s,'Two layers left: at most four possible positions per rank\nand at most four possible ranks per wire',72,190,1136,112,34,C.teal,true);
  text(s,'Thirteen wires, case 115',72,356,1136,50,33,C.ink,true);
  text(s,'Six central wire bounds alone give an UNSAT formula.\nAn independent DRAT check certifies that CNF is UNSAT.',72,429,1136,107,31);
  text(s,'The certificate isolates a structural target: only six central wires.\nNext: extract a short invariant that explains the obstruction.',72,574,1136,80,25,C.amber);

  s=slide(p,'Five layers compress to one','§7 and Appendix B','1:00. This is a specific five-layer eighteen-wire prefix, listed in the report. Each restriction retains only two disjoint real-track pairs. Earlier repeated comparisons become redundant after accounting for their orientation. The seven-wire H7 lemma forces three comparisons in the next original layer.',['d18-search/commuting-prefix-hand-proof.md','depth-hand-proofs/h7-early-profiles.md']);
  text(s,'Four placements leave seven reals each.\nEach five-layer restriction becomes one layer of two gates.',72,185,1136,100,32,C.teal,true);
  table(s,[['Restriction','Real positions after layer five'],['1','C + {a,b,x}'],['2','C + {b,c,y}'],['3','C + {a,b,c}'],['4','C + {a,c,z}']],323,[330,806],49,24);
  text(s,'|C| = 4.  H7 requires three real-real gates in L₆ for every row.',72,600,1136,54,27);

  s=slide(p,'The four retained counts must sum to 12','§7, Lemma 7.1','1:10. Emphasize that we sum retained counts across restrictions, not distinct physical gates. Price each common wire at two, each fork vertex at one, others zero. An edge’s multiplicity across restrictions never exceeds its endpoint prices. Disjoint matching edges cannot spend any vertex price twice.',['d18-search/commuting-prefix-hand-proof.md']);
  table(s,[['Vertices','Price each','Total'],['4 common reals in C','2','8'],['a, b, c','1','3'],['All other positions','0','0']],185,[590,270,276],64,27);
  text(s,'Required: 4 × 3 = 12',72,500,560,70,39,C.amber,true);
  text(s,'Available: 8 + 3 = 11',666,500,542,70,39,C.teal,true);
  text(s,'Every depth-ten completion of this specified five-layer prefix fails.\nFresh check: 20,160 real assignments and 153 edge inequalities.',72,594,1136,64,24);

  s=slide(p,'Concrete upper bounds, with certificates','§9, Table 2','1:10. These are constructed upper bounds, not optimal depths or claimed new records. The 128 and 1024 recipe uses eight-way merging with a sorted-pair base. The middle two use certified halves and standard binary merging. All four were freshly checked by composition.',['https://github.com/abhcs/an_excellent_sort/blob/53034fa080e0b1014dc796281a515ce357765868/SortingNetworks_results_and_proofs.md']);
  table(s,[['Wires','Batcher depth','Our construction','Comparators'],['128','28','26','1,439'],['256','36','34','3,775'],['512','45','43','9,599'],['1024','55','52','23,679']],184,[220,285,350,281],70,27);
  text(s,'Every comparator is covered by a compositional check.\nPriority relative to the full literature has not been established.',72,568,1136,86,27,C.amber);

  s=slide(p,'Save a layer at the merger base case','§9, Theorem 9.1','1:15. M(k,m) merges k sorted lists of length m. Remove the first pair-sorting layer of a known nine-layer 16-sorter: its remaining eight layers merge eight already sorted pairs. Each doubling of list length adds three cleanup layers in parallel with the recursive halves. The finite checker verifies the base and all cleanup zero-count patterns.',['https://github.com/abhcs/an_excellent_sort/blob/53034fa080e0b1014dc796281a515ce357765868/SortingNetworks_results_and_proofs.md']);
  text(s,'M(8, 2) = 8',72,190,1136,68,45,C.teal,true);
  text(s,'M(k, 2m) ≤ M(k, m) + ⌈log₂ k⌉',72,300,1136,65,38);
  text(s,'128 wires:    9 + 17 = 26 layers\n1024 wires:  26 + 26 = 52 layers',72,420,1136,116,35);
  text(s,'Fresh 1024 check: 64 base sorters, 128 pair mergers,\n119 cleanup steps, and all 23,679 comparators accounted for.',72,578,1136,78,26,C.muted);

  s=slide(p,'AKS constants: progress still under review','§10, Table 3','1:10. Do not present a new best constant. The snapshot reports accounting issues and candidate improvements. The roughly 6300 number is an unreviewed agent derivation. The actual open-model contribution is forthcoming and has not been silently merged. The all-size invariant, separator construction, rounding and depth units must be checked.',['https://github.com/abhcs/an_excellent_sort/blob/53034fa080e0b1014dc796281a515ce357765868/main.tex']);
  text(s,'A stage count is not a comparator-layer count',72,190,1136,80,36,C.teal,true);
  text(s,'The current analysis identifies an omitted displacement effect.\nA proposed coefficient near 6,300 is not yet an established bound.',72,330,1136,120,31);
  text(s,'Forthcoming open-model derivation: pending integration.\nNeeded: a complete invariant, separators, rounding, termination,\nand a comparator-depth comparison with published constructions.',72,510,1136,136,28,C.amber);

  s=slide(p,'What the negative results tell us','§3, §5 and §8','1:00. Negative results are mathematical guidance. Distinguish a relaxation survivor from a sorter, and a timeout from UNSAT. The exact 600-second run is a historical experiment, not a current job.',['d18-search/endpoint-cegar.md','d18-search/results/complete18-d10/audit.json','depth-hand-proofs/extension.md']);
  text(s,'Two layer-size caps cannot separate 17 from 18 wires.',72,190,1136,82,32,C.ink,true);
  text(s,'The profile screens leave survivors in all 117 thirteen-wire cases.',72,306,1136,88,31);
  text(s,'Pure blinding cannot universally delete a third layer at width 18.',72,426,1136,87,31);
  text(s,'The 18-wire exact run timed out on one case.\nThe other 410 were not solved. No sorter or refutation resulted.',72,552,1136,100,29,C.amber);

  s=slide(p,'What would constitute the next advance','§8–§11','1:00. End with precise open mathematical tasks. Future collaborator contributions should be merged as separate evidence with explicit dependencies. This slide includes only research goals stated in the report.',['CHECKPOINT.md','d18-search/certificate-guided-frontier.md']);
  text(s,'Force an obstruction across a complete prefix cover',72,192,1136,88,39,C.teal,true);
  text(s,'Mine the central-wire certificates for a short invariant.\nForce the component obstruction across a whole prefix cover.\nExtend compression and complete the remaining H9 hand cases.',72,332,1136,180,31);
  text(s,'Integrate the forthcoming open-model AKS derivation.\nD(18) and a complete simpler logarithmic-depth construction remain open.',72,565,1136,92,29,C.amber);

  s=slide(p,'AI use and formal verification','§2.1, §8–§11 and Appendix E','0:50. Claude and Codex supported the bulk of research and writing; the open math models supported initial analysis. Their forthcoming AKS contribution is pending integration. Both lake build and the direct Lean source check passed for two-layer removal and the halving recurrence, with only propext, Classical.choice and Quot.sound. We plan to formalize all of our work, including the mathematical justification of computational certificates. That is a future goal, not the present verification scope. Model names are team-reported.',['CHECKPOINT.md']);
  text(s,'Claude and Codex: bulk of mathematical work and writing',72,190,1136,85,33,C.teal,true);
  text(s,'Initial analysis: DeepSeek V4.1 Flash and KimiK3.1 Pro',72,305,1136,68,29,C.amber);
  text(s,'Validation: proofs, finite checks, DRAT certificates, and\ncompositional checks of the constructed networks.\nLean verifies the two-layer removal and halving recurrence.',72,421,1136,175,30);
  text(s,'Plan: formalize all of our work in Lean',72,596,1136,52,31,C.teal,true);

  s=slide(p,'Backup: claim dependencies','§1, §6 and §7','Q&A only. This is the important trust boundary: a structural theorem may have a hand proof while its application still depends on H9. A new short proof for a fixed prefix does not close a whole two-layer representative.',['CHECKPOINT.md','d18-search/commuting-prefix-hand-proof.md']);
  table(s,[['Claim','Required evidence'],['Two-layer removal / halving','Hand proof + Lean formalization'],['D(11) ≥ 8 via H9','Transfer + computer-assisted H9'],['Three D17 complete cases','Cover + encoding + DRAT + H9'],['Five-layer D18 example','Track identities + H7 + price proof'],['D(18) ≥ 11','Not established']],190,[530,606],68,25);

  s=slide(p,'Backup: source and scope questions','§1, §8 and Appendix D','Q&A only. Refer to report bibliography and evidence map. The exact research SHA is on the report title block. Full certificate files are in that pinned repository. Fresh checks cover transfer, H7 finite data, third-layer witnesses, the four-restriction direct-value check, and construction certificates.',['https://arxiv.org/abs/1412.5302','https://arxiv.org/abs/1507.01428','https://bertdobbelaere.github.io/sorting_networks.html']);
  text(s,'Prior results',72,190,1136,50,33,C.teal,true);
  text(s,'AKS: logarithmic-depth existence\nBundala et al.: optimal depths through 16 and complete prefix covers\nCodish et al.: depth 10 is optimal at 17 wires\nDobbelaere’s catalogue: depth interval 10–11 at 18 wires',72,268,1136,213,27);
  text(s,'The report is the official record.\nIts evidence map states the exact scope of every computational claim.',72,556,1136,96,29);
  return p;
}
