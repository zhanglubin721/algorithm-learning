"""Deterministic, constraint-aware cases; independent oracles where indicated."""
import random,itertools,collections,math,bisect,copy
R=random.Random(20261030); SPECS=collections.defaultdict(list)
MISSING=object()
def add(i,args,expected=MISSING,tag='边界'):
 c={'name':f'{tag}-{len(SPECS[i])+1:03d}','args':copy.deepcopy(args),'source':'工程构造','oracle':'reference-crosscheck'}
 if expected is not MISSING:c['expected']=copy.deepcopy(expected);c['oracle']='independent-python'
 SPECS[i].append(c)
def generate():
 for n in range(1,18):
  for _ in range(5):
   a=[R.randint(-8,8) for _ in range(n)];positive=[abs(x)+1 for x in a];nonneg=[abs(x) for x in a]
   add(53,[a],max(sum(a[i:j]) for i in range(n) for j in range(i+1,n+1)),'随机穷举')
   add(918,[a],max(sum((a+a)[i:i+k]) for i in range(n) for k in range(1,n+1)),'随机穷举')
   add(152,[a],max(math.prod(a[i:j]) for i in range(n) for j in range(i+1,n+1)),'随机穷举')
   add(41,[a],next(x for x in range(1,n+2) if x not in a),'随机集合')
   add(128,[a],max([0]+[next((k for k in range(1,n+2) if x+k not in a),n+1) for x in set(a)]),'随机集合')
   add(560,[a,R.randint(-10,10)],tag='随机')
   target=R.randint(1,35);lens=[j-i for i in range(n) for j in range(i+1,n+1) if sum(positive[i:j])>=target];add(209,[target,positive],min(lens,default=0),'随机穷举')
   k=R.randint(1,n);add(215,[a,k],sorted(a)[-k],'随机排序')
   w=R.randint(1,n);add(239,[a,w],[max(a[i:i+w]) for i in range(n-w+1)],'随机朴素')
   add(198,[nonneg],max(sum(nonneg[i] for i in range(n) if bits>>i&1) for bits in range(1<<n) if not(bits&(bits<<1))) if n<=12 else MISSING,'随机')
   add(121,[nonneg],max([0]+[nonneg[j]-nonneg[i] for i in range(n) for j in range(i+1,n)]),'随机穷举')
   add(122,[nonneg],sum(max(0,nonneg[i]-nonneg[i-1]) for i in range(1,n)),'随机差分')
   add(42,[nonneg],sum(max(0,min(max(nonneg[:i+1]),max(nonneg[i:]))-nonneg[i]) for i in range(n)),'随机朴素')
   add(84,[nonneg],max(min(nonneg[i:j])*(j-i) for i in range(n) for j in range(i+1,n+1)),'随机穷举')
   add(739,[positive],[next((j-i for j in range(i+1,n) if positive[j]>positive[i]),0) for i in range(n)],'随机朴素')
   add(238,[a],[math.prod(a[:i]+a[i+1:]) for i in range(n)],'随机朴素') if n>=2 else None
   shift=R.randint(0,3*n);add(189,[a,shift],a[-(shift%n):]+a[:-(shift%n)] if shift%n else a,'随机切片')
   add(283,[a],[x for x in a if x!=0]+[0]*a.count(0),'随机过滤')
   target=R.randint(-8,8);add(27,[a,target],{'length':sum(x!=target for x in a),'prefix':sorted([x for x in a if x!=target],key=lambda x:__import__('json').dumps(x))},'随机过滤')
   a.sort();uniq=sorted(set(a));add(26,[a],{'length':len(uniq),'prefix':uniq},'随机去重')
   twice=[x for x in uniq for _ in range(min(2,a.count(x)))];add(80,[a],{'length':len(twice),'prefix':twice},'随机去重')
   target=R.randint(-10,10);ix=[i for i,x in enumerate(a) if x==target];add(34,[a,target],[ix[0],ix[-1]] if ix else [-1,-1],'随机扫描')
   u=sorted(set(a));add(35,[u,target],bisect.bisect_left(u,target),'随机二分')
   add(108,[u],tag='随机平衡树')
   add(219,[a,R.randint(0,n)],tag='随机')
   if n>=2:
    add(11,[nonneg],max((j-i)*min(nonneg[i],nonneg[j]) for i in range(n) for j in range(i+1,n)),'随机穷举')
    add(4,[a[:n//2],a[n//2:]],(a[(n-1)//2]+a[n//2])/2,'随机排序')
   j=R.randrange(len(u));rot=u[j:]+u[:j];add(153,[rot],min(rot),'随机旋转')
   add(33,[rot,target],rot.index(target) if target in rot else -1,'随机扫描')
   if all(a[i]!=a[i-1] for i in range(1,n)):add(162,[a],tag='随机峰值')
   b=sorted(R.randint(-8,8) for _ in range(R.randint(0,10)));add(88,[a+[0]*len(b),len(a),b,len(b)],sorted(a+b),'随机排序')
   majority=R.randint(-9,9);v=[majority]*(n+1)+a;R.shuffle(v);add(169,[v],majority,'随机多数')
   if n<=10:
    add(15,[a],[list(x) for x in sorted({tuple(sorted(t)) for t in itertools.combinations(a,3) if sum(t)==0})],'随机穷举')
   if n<=9:
    p=a[:];R.shuffle(p);add(31,[p],tag='随机排列')
 for _ in range(100):
  a=R.sample(range(-100,100),R.randint(2,15));i,j=R.sample(range(len(a)),2);t=a[i]+a[j]
  if sum(a[x]+a[y]==t for x in range(len(a)) for y in range(x+1,len(a)))==1:
   add(1,[a,t],[i,j],'随机唯一解');b=sorted(a);ii,jj=sorted([b.index(a[i])+1,b.index(a[j])+1]);add(167,[b,t],[ii,jj],'随机唯一解')
 for n in range(0,20):
  for _ in range(4):
   s=''.join(R.choice('abca') for _ in range(n));t=''.join(R.choice('abc') for _ in range(R.randint(1,6)))
   add(3,[s],max([0]+[j-i for i in range(n) for j in range(i+1,n+1) if len(set(s[i:j]))==j-i]),'随机穷举')
   if s:
    pals=[s[i:j] for i in range(n) for j in range(i+1,n+1) if s[i:j]==s[i:j][::-1]];add(5,[s],max(pals,key=len),'随机穷举')
    add(763,[s],tag='随机')
   add(392,[t,s],iter_sub(t,s),'随机')
   add(242,[s,t],collections.Counter(s)==collections.Counter(t),'随机计数')
   add(383,[t,s],not(collections.Counter(t)-collections.Counter(s)),'随机计数')
   if s:
    add(438,[s,t],[i for i in range(n-len(t)+1) if sorted(s[i:i+len(t)])==sorted(t)],'随机计数')
    add(28,[s,t],s.find(t),'随机查找')
    windows=[s[i:j] for i in range(n) for j in range(i+1,n+1) if not(collections.Counter(t)-collections.Counter(s[i:j]))];add(76,[s,t],min(windows,key=len,default=''),'随机穷举')
   add(72,[s,t],tag='随机编辑')
 for x in [0,1,2,3,4,8,9,10,99,100,2147395599,2147483647]:
  add(69,[x],math.isqrt(x));add(9,[x],str(x)==str(x)[::-1]);add(172,[x],sum(x//(5**k) for k in range(1,16)))
 for x in [-121,-1,-2147483648]:add(9,[x],False)
 for x in [1,2,3,7,8,15,31,32,127,128,2147483647]:add(191,[x],x.bit_count());add(190,[x],int(f'{x:032b}'[::-1],2) if int(f'{x:032b}'[::-1],2)<2**31 else int(f'{x:032b}'[::-1],2)-2**32)
 for n in range(1,39):
  a,b=1,1
  for _ in range(n):a,b=b,a+b
  add(70,[n],a)
 for n in range(1,80):
  dp=[0]+[1000]*n
  for x in range(1,n+1):dp[x]=1+min(dp[x-j*j] for j in range(1,math.isqrt(x)+1))
  add(279,[n],dp[n])
 for x in [1,4,9,40,49,90,99,400,900,1994,3999]:add(12,[x]);
 for s in ['I','III','IV','IX','XL','XC','CD','CM','MCMXCIV','MMMCMXCIX']:add(13,[s])
 for a,b in itertools.product([0,1,3,7,15,63],repeat=2):add(67,[bin(a)[2:],bin(b)[2:]],bin(a+b)[2:])
 for n in [0,1,9,10,99,999,12345]:add(66,[[int(c) for c in str(n)]],[int(c) for c in str(n+1)])
 for x,n in [(2.,0),(2.,-2),(-2.,3),(-2.,4),(0.,1),(1.,-2147483648),(-1.,2147483647),(1.00001,123)]:add(50,[x,n],x**n)
 for lo in range(0,30):
  for hi in range(lo,lo+5):
   v=lo
   for x in range(lo+1,hi+1):v&=x
   add(201,[lo,hi],v,'随机穷举')
 for _ in range(30):
  vals=R.sample(range(-200,200),R.randint(1,10));special=vals.pop();a=[x for x in vals for _ in range(2)]+[special];R.shuffle(a);add(136,[a],special);a=[x for x in vals for _ in range(3)]+[special];R.shuffle(a);add(137,[a],special)
  amount=R.randint(0,50);coins=sorted(set(R.randint(1,15) for _ in range(5)));dp=[0]+[999]*amount
  for v in range(1,amount+1):dp[v]=min([999]+[dp[v-c]+1 for c in coins if c<=v])
  add(322,[coins,amount],-1 if dp[amount]>=999 else dp[amount],'随机动态规划')
  a=[R.randint(1,8) for _ in range(R.randint(1,12))];sums={0}
  for v in a:sums|={x+v for x in sums}
  add(416,[a],sum(a)%2==0 and sum(a)//2 in sums,'随机子集')
 for n in range(1,8):
  for k in range(1,n+1):add(77,[n,k],[list(x) for x in itertools.combinations(range(1,n+1),k)],'组合枚举')
  a=list(range(n));add(78,[a],[list(t) for k in range(n+1) for t in itertools.combinations(a,k)],'子集枚举')
  if n<=6:add(46,[a],[list(x) for x in itertools.permutations(a)],'排列枚举')
 for n in range(1,8):add(22,[n]);add(51,[n]);add(52,[n])
 for d in ['2','7','23','29','79','234','999']:add(17,[d])
 for a,t in [([2],1),([2],2),([2,3],7),([3,5],15),([2,3,6,7],7),([2,4],9)]:add(39,[a,t])
 for n in range(1,9):
  for m in range(1,7):add(62,[n,m],math.comb(n+m-2,n-1))
 for n in range(1,8):
  for _ in range(4):
   grid=[[R.randint(0,5) for _ in range(n)] for _ in range(n)];add(64,[grid]);add(54,[grid]);add(48,[grid]);add(73,[grid]);b=[[R.randint(0,1) for _ in range(n)] for _ in range(n)];add(289,[b]);add(63,[b]);add(221,[[[str(x) for x in row] for row in b]]);add(200,[[[str(x) for x in row] for row in b]]);add(130,[[['O' if x else 'X' for x in row] for row in b]]);add(994,[[[R.randint(0,2) for _ in range(n)] for _ in range(n)]]);add(74,[[list(range(i*n,(i+1)*n)) for i in range(n)],R.randint(-1,n*n)]);add(240,[[list(range(i*n,(i+1)*n)) for i in range(n)],R.randint(-1,n*n)])
 for n in [1,2,4,8]:
  for _ in range(4):add(427,[[[R.randint(0,1) for _ in range(n)] for _ in range(n)]])
 for a in [[],[1],[1,2],[2,1],[-1,0,1],[1,1,2,2,3],[9,8,7,6,5,4]]:
  add(206,[a],a[::-1]);add(148,[a],sorted(a));add(234,[a],a==a[::-1]) if a else None;add(24,[a]);add(86,[a,2]);add(61,[a,0]);add(61,[a,9]);add(82,[sorted(a)]);
  for pos in [-1]+list(range(len(a))):add(141,[a,pos],pos>=0);add(142,[a,pos],pos)
  if a:
   for k in range(1,len(a)+1):add(25,[a,k]);add(19,[a,k],a[:len(a)-k]+a[len(a)-k+1:])
   add(92,[a,1,len(a)],a[::-1])
 for a,b in [([],[]),([],[1]),([1],[]),([1,2,4],[1,3,4]),([-3,0,9],[-5,2,8])]:add(21,[a,b],sorted(a+b))
 for a in [[],[[]],[[1],[0]],[[1,3,5],[2,4,6],[]]]:add(23,[a],sorted(sum(a,[])))
 for x,y in [(0,0),(9,1),(999,1),(128,875),(999999,999999)]:add(2,[[int(c) for c in str(x)[::-1]],[int(c) for c in str(y)[::-1]]],[int(c) for c in str(x+y)[::-1]])
 for tree in [[],[1],[1,2,3],[1,None,2,None,3],[0,-1,1],[-10,9,20,None,None,15,7],[1,2,2,3,4,4,3]]:
  for i in [104,226,101,199,637,102,103,94,543,114,117]:
   if tree or i not in [101,637]:add(i,[tree])
  add(100,[tree,tree],True);add(100,[tree,[]],not tree);add(112,[tree,3]);add(437,[tree,3])
  if tree:add(124,[tree])
 for tree in [[1],[2,1,3],[4,2,6,1,3,5,7],[0,-2,3,None,-1]]:
  add(98,[tree],True)
  if len(tree)>1:add(530,[tree])
  for k in range(1,sum(x is not None for x in tree)+1):add(230,[tree,k],sorted(x for x in tree if x is not None)[k-1])
 for tree in [[5,1,4,None,None,3,6],[2,2,3],[1,2,3]]:add(98,[tree],False)
 for n in range(0,32):add(222,[list(range(n))],n)
 for tree in [[1],[1,2,3],[4,9,0,5,1]]:add(129,[tree])
 for a,b in [([1],[1]),([1,2],[2,1]),([3,9,20,15,7],[9,3,15,20,7])]:add(105,[a,b])
 for a,b in [([1],[1]),([2,1],[2,1]),([9,3,15,20,7],[9,15,7,20,3])]:add(106,[a,b])
 add(236,[[3,5,1,6,2,0,8,None,None,7,4],5,4],5)
 for i in [133]:
  for adj in [[],[[]],[[2],[1]],[[2,3],[1,3],[1,2]],[[2,4],[1,3],[2,4],[1,3]]]:add(i,[adj])
 for a in [[],[[1,None]],[[1,0]],[[1,1],[2,0]],[[7,None],[13,0],[11,4],[10,2],[1,0]]]:add(138,[a])
 add(160,[0,[1,2],[3,4],2,2],None);add(160,[3,[1,2,3],[4,3],2,1],3);add(160,[1,[1],[1],0,0],1)
 return SPECS

def iter_sub(s,t):
 it=iter(t);return all(c in it for c in s)
if __name__=='__main__':
 generate();print('specs',len(SPECS),sum(map(len,SPECS.values())))
