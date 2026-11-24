"""D(17) probe (efficient-prefixes.md section 10): which exceptional prefix classes are settled without SAT?
(i) the class also contains a non-exceptional prefix (covered by the descent lemma; subsumption);
(ii) some sentinel residual of an exceptional member lands in a class of the lower family LOWER.bin
     (classcount output; all its classes are settled once the lower statement holds).
usage: exclookup.py EXCRES.txt LOWER.bin [LEFT_OUT.txt]"""
import sys, struct
lower = set()
data = open(sys.argv[2], 'rb').read()
for k in range(0, len(data), 16):
    h1, h2 = struct.unpack('<QQ', data[k:k + 16]); lower.add(f'{h1:016x}{h2:016x}')
tot = covered = viares = 0; left = []
for line in open(sys.argv[1]):
    f = line.split(); tot += 1
    if f[1] == '1':
        covered += 1
    elif any(h in lower for h in f[2:]):
        viares += 1
    else:
        left.append(f[0])
print(f'{tot} classes; {covered} contain a non-exceptional prefix; of the {tot - covered} exceptional-only classes, '
      f'{viares} have a residual in a lower-family class, {len(left)} remain')
if len(sys.argv) > 3:
    open(sys.argv[3], 'w').write('\n'.join(left) + '\n')
