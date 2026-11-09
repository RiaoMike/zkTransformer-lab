"""Small exact-arithmetic labs. Teaching code, NOT a secure proof system.
No PCS, no hiding, and fixed verifier challenges. All tensors use little-endian
Boolean coordinates: flat_index = b0 + 2*b1 + 4*b2 + ... .
"""
from itertools import product
from math import prod, exp, log
import argparse

P = 101

def bits(index, n):
    return [(index >> j) & 1 for j in range(n)]

def eq(x, y):
    assert len(x) == len(y)
    return prod((a*b + (1-a)*(1-b)) % P for a,b in zip(x,y)) % P

def fold(table, r):
    assert len(table) >= 2 and len(table) % 2 == 0
    return [(a + r*(b-a)) % P for a,b in zip(table[::2],table[1::2])]

def mle(table, point):
    assert len(table) == 1 << len(point)
    work = list(table)
    for r in point:
        work = fold(work,r)
    return work[0] % P

def mle_definition(table, point):
    return sum(v*eq(point,bits(i,len(point))) for i,v in enumerate(table)) % P

def interpolate(values, x):
    """Degree <= len(values)-1; values are evaluations at 0,1,...,d."""
    total = 0
    for j,y in enumerate(values):
        numerator = denominator = 1
        for k in range(len(values)):
            if j != k:
                numerator = numerator*(x-k) % P
                denominator = denominator*(j-k) % P
        total += y*numerator*pow(denominator,-1,P)
    return total % P

def prove_sumcheck(tables, challenges):
    assert tables and all(len(t)==1<<len(challenges) for t in tables)
    arrays = [list(t) for t in tables]
    messages = []
    for r in challenges:
        message = []
        for t in range(len(arrays)+1):
            bound = [fold(a,t) for a in arrays]
            message.append(sum(prod(row) for row in zip(*bound)) % P)
        messages.append(message)
        arrays = [fold(a,r) for a in arrays]
    return messages

def verify_sumcheck(claim, messages, challenges, degree, oracle):
    if len(messages) != len(challenges):
        return False
    current = claim % P
    for msg,r in zip(messages,challenges):
        if len(msg) != degree+1 or (msg[0]+msg[1])%P != current:
            return False
        current = interpolate(msg,r)
    # In the real protocol this value must be authenticated by PCS / recursion.
    return current == oracle(challenges) % P

def classify(equation):
    lhs,out = equation.split('->')
    ins = lhs.split(',')
    assert all(len(set(s))==len(s) for s in ins), 'Diagonal indices excluded'
    assert len(set(out))==len(out) and set(out)<=set(''.join(ins))
    labels = list(dict.fromkeys(''.join(ins)))
    once = [c for c in out if sum(c in s for s in ins)==1]
    multi = [c for c in out if sum(c in s for s in ins)>1]
    summed = [c for c in labels if c not in out]
    return ins,out,once,multi,summed

def compile_toy(equation, tables, challenge):
    """Each index has dimension 2. Explicit broadcast is educational, not optimal."""
    ins,out,once,multi,summed = classify(equation)
    assert len(tables)==len(ins) and len(challenge)==len(out)
    assert all(len(t)==1<<len(s) for t,s in zip(tables,ins))
    r = dict(zip(out,challenge))
    active = multi+summed
    polys = [[] for _ in ins]
    eq_table = []
    for i in range(1<<len(active)):
        env = dict(zip(active,bits(i,len(active))))
        env.update({c:r[c] for c in once})
        for poly,t,spec in zip(polys,tables,ins):
            poly.append(mle(t,[env[c] for c in spec]))
        eq_table.append(eq([r[c] for c in multi],[env[c] for c in multi]))
    polys.append(eq_table)
    return active,polys

def einsum_toy(equation, tables):
    ins,out,_,_,summed = classify(equation)
    result=[]
    for i in range(1<<len(out)):
        env=dict(zip(out,bits(i,len(out))))
        total=0
        for j in range(1<<len(summed)):
            env.update(zip(summed,bits(j,len(summed))))
            total += prod(t[sum(env[c]<<k for k,c in enumerate(spec))]
                          for t,spec in zip(tables,ins))
        result.append(total%P)
    return result

def lesson1():
    table=[1,2,3,4]
    assert mle(table,[2,3]) == mle_definition(table,[2,3]) == 9
    for i in range(4):
        assert mle(table,bits(i,2))==table[i]
    print('MLE [1,2,3,4] at (2,3) =',mle(table,[2,3]))

def lesson2():
    a,b=[1,2],[3,5]
    c=[x*y%P for x,y in zip(a,b)]
    wrong=mle(a,[2])*mle(b,[2])%P
    correct=mle(c,[2])
    repaired=sum(eq([2],[i])*a[i]*b[i] for i in range(2))%P
    assert (correct,wrong,repaired)==(17,21,17)
    print('output MLE = 17; product of MLEs = 21; eq repair = 17')

def lesson3():
    cases=[('ij,jk->ik',[[1,2,3,4],[5,6,7,8]],[2,3]),
           ('bij,bjk->bik',[list(range(1,9)),list(range(11,19))],[2,3,4]),
           ('i,i->i',[[1,2],[3,5]],[2]),
           ('ij->i',[[1,2,3,4]],[2]),
           ('ij->ji',[[1,2,3,4]],[2,3]),
           ('ij,jk,kl->il',[list(range(1,5))]*3,[2,3]),
           ('ij,j->',[[1,2,3,4],[5,6]],[])]
    for equation,tables,r in cases:
        active,polys=compile_toy(equation,tables,r)
        expected=mle(einsum_toy(equation,tables),r)
        actual=sum(prod(row) for row in zip(*polys))%P
        assert actual==expected
        print(equation,'sum variables:',active,'claim:',expected)

def lesson4():
    active,tables=compile_toy('bij,bjk->bik',
        [list(range(1,9)),list(range(11,19))],[2,3,4])
    claim=sum(prod(row) for row in zip(*tables))%P
    challenges=[7,11]
    proof=prove_sumcheck(tables,challenges)
    oracle=lambda r: prod(mle(t,r) for t in tables)%P
    assert verify_sumcheck(claim,proof,challenges,3,oracle)
    assert not verify_sumcheck(claim+1,proof,challenges,3,oracle)
    corrupt=[m[:] for m in proof]
    corrupt[0][0]=(corrupt[0][0]+1)%P
    assert not verify_sumcheck(claim,corrupt,challenges,3,oracle)
    assert not verify_sumcheck(claim,proof,challenges,3,lambda r:oracle(r)+1)
    for i,msg in enumerate(proof):
        print('round',i+1,'evaluations at 0,1,2,3:',msg)
    print('accepted honest transcript; rejected wrong claim/message/final oracle')

def lesson5():
    # Table T[j]=j and T[j]=2^j. These are field identities.
    r=[2,3,4]
    range_table=list(range(8))
    power_table=[pow(2,j,P) for j in range(8)]
    assert mle(range_table,r)==sum((1<<j)*x for j,x in enumerate(r))%P
    closed=prod(1+(pow(2,1<<j,P)-1)*x for j,x in enumerate(r))%P
    assert mle(power_table,r)==closed
    selection=[1,3,0,2]
    # a(i,j) is one-hot in j for each Boolean row i.
    a=[int(selection[i]==j) for j in range(4) for i in range(4)]
    row_point=[2,3]
    lookup_sum=sum(mle(a,row_point+bits(j,2))*j for j in range(4))%P
    assert lookup_sum==mle(selection,row_point)
    print('range/power table closed forms and one-hot lookup identity passed')

def lesson6():
    # Numerical illustration only: NOT a field proof or exact repository quantization.
    scale=1<<15
    ln2_int=round(scale*log(2))
    for q in [0,-32768,-100000,-300000]:
        k=int((-q/ln2_int)+0.5)
        remainder=q+k*ln2_int
        assert 0<=k<=15 and abs(remainder)<=ln2_int/2
        u=remainder/scale
        approximation=(1<<(15-k))*(1+u+u*u/2+u*u*u/6)
        target=scale*exp(q/scale)
        print(f'q={q}, k={k}, remainder={remainder}, approx={approximation:.6f}, exact={target:.6f}')

def self_test():
    import random
    rng=random.Random(2026)
    for n in range(1,5):
        for _ in range(12):
            t=[rng.randrange(P) for _ in range(1<<n)]
            r=[rng.randrange(P) for _ in range(n)]
            assert mle(t,r)==mle_definition(t,r)
            tables=[t,[rng.randrange(P) for _ in t]]
            h=sum(a*b for a,b in zip(*tables))%P
            messages=prove_sumcheck(tables,r)
            assert verify_sumcheck(h,messages,r,2,lambda x:prod(mle(a,x) for a in tables))
    print('48 randomized MLE/sumcheck cross-checks passed')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('lesson',choices=['all','1','2','3','4','5','6'],default='all',nargs='?')
    args=parser.parse_args()
    lessons=[lesson1,lesson2,lesson3,lesson4,lesson5,lesson6]
    for index,lesson in enumerate(lessons,1):
        if args.lesson in ('all',str(index)):
            print(f'Lesson {index}'); lesson()
    if args.lesson=='all': self_test()
