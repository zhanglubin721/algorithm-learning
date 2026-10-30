import json,pathlib,random,math
R=pathlib.Path(__file__).resolve().parents[1];idx=json.loads((R/'catalog/canonical.json').read_text());rng=random.Random(20261030)
def add(id,args,expected):
 p=R/idx[str(id)]/'测试/cases.json';cs=json.loads(p.read_text());cs=[c for c in cs if c['name']!='规模边界'];cs.append({'name':'规模边界','args':args,'expected':expected,'source':'工程约束内构造','oracle':'independent-python'});p.write_text(json.dumps(cs,ensure_ascii=False,indent=2))
a=list(range(1,10001));add(1,[a,19999],[9998,9999])
a=list(range(1,100001));rng.shuffle(a);add(128,[a],100000);add(41,[a],100001);add(215,[a,50000],50001)
add(53,[[1]*100000],100000);add(560,[[0]*20000,0],200010000)
a=list(range(100000));add(239,[a,50000],list(range(49999,100000)))
add(238,[[1]*10000],[1]*10000)
p=R/idx['152']/'测试/cases.json';cs=json.loads(p.read_text());out=[]
for c in cs:
 a=c['args'][0]
 if all(-2**31<=math.prod(a[i:j])<2**31 for i in range(len(a)) for j in range(i+1,len(a)+1)):out.append(c)
p.write_text(json.dumps(out,ensure_ascii=False,indent=2));print('规模边界已补；乘积约束已核对')
