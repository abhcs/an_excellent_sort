"""Exact arithmetic and rounding audit of the collaborator's AKS parameter note.

This checks the parameter application, not Chvatal's separator-existence and
outsider-invariant proofs, and does not construct the enormous network or
constitute Lean verification. Uses Python's standard library only.
"""
from fractions import Fraction as F
from math import factorial
import hashlib
import json
from pathlib import Path

k, A, nu, M = 64, 2048, F(1,32), 2**59
mu, deltaF, epsF, epsB, delta = F(1,2**28), F(128,4095), F(1,20000000), F(467,10**10), F(8,10**10)
B = lambda p: p*(p+1)//2
assert M >= 32*A*A*k*k == 2**39

# Recover each block shape from the Section 5 formulas, not the claimed table.
shapes = [('top-advance',0,1,49,2**55,0),
          ('top-retreat',k//2,A*k/nu-1,27,2**55,2**32),
          ('interior',A*nu*k-1,2*A*A*k-2*A*nu,20,2**55-2**21,4095*2**20)]
for h in range(22):
    shapes.append((f'bottom-advance-h{h}',A*nu*k-1,F(2*A*A*k,2**h)-2*A*nu,20+h,2**55-2**(21+h),4095*2**(20+h)))
checked=[]
for name,f0,b0,want_r,want_m,want_f in shapes:
    assert F(f0).denominator == F(b0).denominator == 1
    f0,b0=int(f0),int(b0)
    m0=2*f0+k*b0
    assert 0 <= f0 and 0 < b0 and m0 < 2*A*A*k*k
    r=0
    while 2**(r+1)*m0 <= M//16: r+=1
    m,f,b=2**r*m0,2**r*f0,2**r*b0
    assert (r,m,f)==(want_r,want_m,want_f),name
    assert M//32 < m <= M//16 and m==2*f+k*b and m>=100
    assert f==0 or (f>=10 and f%2==0)
    checked.append(dict(shape=name,m0=m0,r=r,m=m,f=f,b=b))
mmin=min(x['m'] for x in checked); fmin=min(x['f'] for x in checked if x['f'])
assert mmin==2**55-2**42 and fmin==4095*2**20
# a>M and m<=M/16 imply n=a/m>16. All block-size ratios are dyadic.

# Rational analytic bounds, avoiding floating-point logarithm comparisons.
ln2_upper=sum((F(2,(2*j+1)*3**(2*j+1)) for j in range(4)),F(0))+F(1,4*3**9)
assert ln2_upper<F(694,1000)
assert F(2, mmin)*(1+55*F(694,1000)) < epsB**2
x=F(4,3)
exp43_upper=sum((x**j/F(factorial(j)) for j in range(11)),F(0))+x**11/F(factorial(11))*F(9,8)
assert exp43_upper<F(19,5)<F(12,100)/deltaF
# This proves L=ln(.12/(e*deltaF))>1/3.
exp35_lower=sum((F(35)**j/F(factorial(j)) for j in range(46)),F(0))
assert exp35_lower>300000*fmin and 300000>3*3**5
assert F(212,fmin-2)<epsF and F(12,fmin)<epsF and deltaF<F(1,25)
assert (1/epsF).denominator==1
# f -> 2(1+ln(3e^5 f)/L)/(f-2) decreases: the derivative's
# numerator is (f-2)/f - L - ln(3e^5 f), which is negative for f>=fmin.
epsroot=mu/k
assert epsroot==F(1,2**34)
assert F(2,2**75)*(1+75*F(694,1000)) < epsroot**2
assert 2**75%k==0 and 2**(6*14-75)>=16

# Check the original (4.1)--(4.5), including both equalities and denominator.
assert delta*k*A<1
v42=(1+(k-1)*delta*k*A*A/(1-delta**2*k*k*A*A)+(A*nu*k-2*A*nu+1)/(2*mu*A*A*k*k)+epsB/mu)/(A*nu)+delta*A*k/nu
v45=epsF/(A*nu)+delta**2*A*k/nu
assert v42<F(911,1000)<1
assert mu==nu/(A*k*k)==deltaF*(A*nu*k-1)/(2*A*A*k*k)
assert v45==F('7.8393435456e-10')<delta
assert mu*delta*2*A*A*k*k==F('1.024e-7')<1
assert B(59)==1770<=2*B(55)==3080

def ceil_fraction(num,den): return -((-num)//den)
def level(num,den,t,nonnegative=False):
    v=ceil_fraction(num,den)
    if nonnegative: v=max(v,0)
    return v+(t-v)%2

def direct_meeting(d):
    for t in range(2,4*d+10):
        a=level(5*t-6*d+25,11,t,True)
        w=level(5*t+12,17,t)
        if a==w:return t,d-a
        assert a<w
    raise AssertionError(d)

# Exhaust the finite q/u residue reduction, independently of direct rounding.
residues=[]
expected=[(14,30,4,-88,-51123),(15,33,4,-90,-52355),(16,35,5,-97,-56466),(17,38,5,-99,-57698),(18,41,5,-101,-58930)]
for d,tf,q,z,offset in expected:
    candidates=[]
    for qq in range(-3,6):
        i=d-qq
        for u in range(-45,1):
            if max(-46,6*qq-47)<u<=min(-12,6*qq-25) and (u+12*i)%10==0:
                t=(17*i+u)//5
                if t>=2:candidates.append((t,qq,u))
    t,qq,u=min(candidates)
    assert (t,qq)==direct_meeting(d)==(tf,q)
    assert 5*tf-17*d==z and z < -79
    depth=2*B(75)+(tf-1)*2*B(55)+B(6*(q+1))
    assert depth-10472*d==offset
    residues.append(dict(d=d,tf=tf,q=q,u=u,depth=depth,offset=offset))
# Cross-check 500 dimensions. The all-d conclusion uses the proved period,
# not extrapolation from this bounded range.
for d in range(14,514):
    base=expected[(d-14)%5]
    assert direct_meeting(d)==(base[1]+17*((d-base[0])//5),base[2])
assert 17*3080==5*10472
assert max(x['offset'] for x in residues)==-51123
assert F(10472,6)==F(5236,3) and -51123+10472==-40651
coefficient_gain=1-F(5236,3)/1830
crossover=F(58657-40651)/(1830-F(5236,3))
assert crossover==F(27009,127)
source=Path(__file__).resolve().parents[1]/'collaborator/sorting_network_depth_bound-source.txt'
result=dict(status='PASS',scope='Exact parameter and rounding audit conditional on the cited Chvatal theorems; not Lean verification or an instantiated network test.',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),separator_shapes=checked,shape_count=len(checked),m_min=mmin,f_min=fmin,condition_4_2_normalized=str(v42),condition_4_2_decimal=float(v42),condition_4_5=str(v45),stopping_rows=residues,rounding_dimensions_checked=[14,513],all_dimensions_argument='Five residue classes with d -> d+5, t_f -> t_f+17 and q unchanged; all other possible q give later meetings.',bound=dict(coefficient='5236/3',constant=-40651,minimum_N='2^79'),coefficient_reduction_percent=float(100*coefficient_gain),full_bound_crossover_log2N=str(crossover))
print(json.dumps(result,indent=2))
