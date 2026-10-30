from test_specs import *
from functools import lru_cache

def extend():
 for _ in range(70):
  n=R.randint(1,12);a=[R.randint(0,5) for _ in range(n)];dist=[999]*n;dist[0]=0
  for i in range(n):
   for j in range(i+1,min(n,i+a[i]+1)):dist[j]=min(dist[j],dist[i]+1)
  add(55,[a],dist[-1]<999,'随机BFS')
  if dist[-1]<999:add(45,[a],dist[-1],'随机BFS')
  add(274,[a],max(h for h in range(n+1) if sum(x>=h for x in a)>=h),'随机定义')
  vals=[R.randint(0,10) for _ in range(n)];add(300,[vals],max(len(t) for k in range(n+1) for t in itertools.combinations(vals,k) if all(t[i]<t[i+1] for i in range(len(t)-1))),'随机穷举')
  b=[R.randint(0,5) for _ in range(n)];valid=[]
  for st in range(n):
   balance=0
   for j in range(n):balance+=a[(st+j)%n]-b[(st+j)%n];
   running=0;ok=True
   for j in range(n):
    running+=a[(st+j)%n]-b[(st+j)%n]
    if running<0:ok=False;break
   if ok:valid.append(st)
  if len(valid)<=1:add(134,[a,b],valid[0] if valid else -1,'随机模拟')
  add(135,[vals],tag='随机评分')
  for k in [1,2,3]:
   @lru_cache(None)
   def profit(i,left,held):
    if i==len(vals):return -10**9 if held else 0
    ans=profit(i+1,left,held)
    if held:ans=max(ans,vals[i]+profit(i+1,left,False))
    elif left:ans=max(ans,-vals[i]+profit(i+1,left-1,True))
    return ans
   add(188,[k,vals],profit(0,k,False),'随机状态穷举')
   if k==2:add(123,[vals],profit(0,2,False),'随机状态穷举')
  colors=[x%3 for x in vals];add(75,[colors],sorted(colors),'随机排序')
  m=R.randint(1,12);dup=R.randint(1,m);v=list(range(1,m+1))+[dup];R.shuffle(v);add(287,[v],dup,'随机构造')
  freq={x:i+1 for i,x in enumerate(R.sample(range(-50,50),R.randint(1,8)))};arr=[x for x,f in freq.items() for _ in range(f)];R.shuffle(arr);k=R.randint(1,len(freq));add(347,[arr,k],sorted(freq,key=freq.get,reverse=True)[:k],'随机频数')
  x=sorted(R.randint(-6,6) for _ in range(R.randint(1,8)));y=sorted(R.randint(-6,6) for _ in range(R.randint(1,8)));k=R.randint(1,min(15,len(x)*len(y)));pairs=sorted([[i,j] for i in x for j in y],key=lambda t:sum(t));add(373,[x,y,k],pairs[:k],'随机笛卡尔积')
 for n in range(1,31):
  rows=[[math.comb(i,j) for j in range(i+1)] for i in range(n)];add(118,[n],rows,'组合公式')
 for a in [[],[''],['a'],['ab','a'],['flower','flow','flight'],['dog','racecar','car'],['same','same']]:
  if a:add(14,[a])
 for s in ['a','hello world','   fly me   to   the moon  ','a ','  z']:
  add(58,[s],len(s.split()[-1]));add(151,[s],' '.join(s.split()[::-1]))
 for s in ['', ' ', 'a', 'Aa', 'ab', 'A man, a plan, a canal: Panama','0P','race a car']:
  v=''.join(c.lower() for c in s if c.isalnum());add(125,[s],v==v[::-1])
 for s in ['A','AB','PAYPALISHIRING','ABCDEFGHIJKLMNO']:
  for rows in [1,2,3,4,8]:add(6,[s,rows])
 for words,w in [(['a'],1),(['a','b'],3),(['This','is','an','example','of','text','justification.'],16),(['abcdefgh','i','jk'],8),(['a','b','c','d','e'],3)]:add(68,[words,w])
 for s,words in [('a',['a']),('aaaaaa',['aa','aa']),('barfoofoobarthefoobarman',['bar','foo','the']),('wordgoodgoodgoodbestword',['word','good','best','good'])]:add(30,[s,words])
 for a,b in [('egg','add'),('foo','bar'),('ab','aa'),('paper','title'),('a','a')]:add(205,[a,b])
 for p,s in [('abba','dog cat cat dog'),('abba','dog cat cat fish'),('aaaa','dog cat cat dog'),('ab','dog dog'),('a','a b')]:add(290,[p,s])
 for a in [[''],['a'],['eat','tea','tan','ate','nat','bat'],['aa','aa','a'],['ab','ba','abc','cab']]:add(49,[a])
 for n in [1,2,4,7,19,20,100,999,2147483647]:
  seen=set();x=n
  while x!=1 and x not in seen:seen.add(x);x=sum(int(c)**2 for c in str(x))
  add(202,[n],x==1)
 for a in [[],[0],[-2147483648,2147483647],[0,1,2,4,5,7],[-3,-2,-1,1,3]]:add(228,[a])
 for a in [[[1,3]],[[1,4],[4,5]],[[1,10],[2,3]],[[1,3],[2,6],[8,10],[15,18]],[[2,3],[4,5]]]:
  add(56,[a]);add(452,[a]);
 for a,b in [([],[1,2]),([[1,3]],[2,5]),([[1,2],[5,7]],[3,4]),([[1,2],[3,5],[6,7],[8,10],[12,16]],[4,8])]:add(57,[a,b])
 for s in ['()','()[]{}','(]','([)]','{[]}','(',')))','((()))']:add(20,[s])
 for s in ['/','/home/','/../','/home//foo/','/a/./b/../../c/','/.../a/../b']:add(71,[s])
 for tokens in [['1'],['2','1','+','3','*'],['4','13','5','/','+'],['-7','3','/'],['7','-3','/'],['3','4','-']]:add(150,[tokens])
 for s in ['0','1 + 1',' 2-1 + 2 ','(1+(4+5+2)-3)+(6+8)','-2+1','1-(-2)','-(3+(4-1))']:add(224,[s])
 for s in ['1[a]','3[a2[c]]','2[abc]3[cd]ef','10[a]','abc3[cd]xyz']:add(394,[s])
 for s in ['(',')','()','(()',')()())','()(())','()(()','((()))','']:
  best=0
  for i in range(len(s)):
   b=0
   for j in range(i,len(s)):
    b+=1 if s[j]=='(' else -1
    if b<0:break
    if b==0:best=max(best,j-i+1)
  add(32,[s],best)
 for s in ['a','aa','ab','aab','abba','banana']:add(131,[s])
 for s,words in [('a',['a']),('leetcode',['leet','code']),('catsandog',['cats','dog','sand','and','cat']),('aaaaaaa',['aaaa','aaa']),('ab',['a'])]:add(139,[s,words])
 for _ in range(35):
  a=''.join(R.choice('abc') for _ in range(R.randint(1,7)));b=''.join(R.choice('abc') for _ in range(R.randint(1,7)))
  subs={''.join(t) for k in range(len(a)+1) for t in itertools.combinations(a,k)};add(1143,[a,b],max(len(s) for s in subs if iter_sub(s,b)),'随机子序列枚举')
  add(97,[a,b,a+b],True);add(97,[a,b,a+b+'x'],False)
 for n in range(1,9):add(120,[[[R.randint(-9,9) for _ in range(i+1)] for i in range(n)]])
 for n,edges in [(1,[]),(2,[[1,0]]),(2,[[1,0],[0,1]]),(4,[[1,0],[2,0],[3,1],[3,2]]),(3,[[1,0],[2,1],[0,2]])]:add(207,[n,edges]);add(210,[n,edges])
 for n in [2,3,4]:
  board=[[-1]*n for _ in range(n)];add(909,[board]);board[-1][1]=n*n;add(909,[board])
 for a,b,bank in [('AACCGGTT','AACCGGTA',['AACCGGTA']),('AACCGGTT','AACCGGTA',[]),('AAAAACCC','AACCCCCC',['AAAACCCC','AAACCCCC','AACCCCCC'])]:add(433,[a,b,bank])
 for a,b,words in [('hit','cog',['hot','dot','dog','lot','log','cog']),('hit','cog',['hot','dot','dog','lot','log']),('a','c',['a','b','c'])]:add(127,[a,b,words])
 add(399,[[['a','b'],['b','c']],[2.0,3.0],[['a','c'],['b','a'],['a','e'],['a','a'],['x','x']]], [6.,.5,-1.,1.,-1.])
 for board,word in [([['A']],'A'),([['A']],'B'),([['A','B'],['C','D']],'ABDC'),([['A','A']],'AAA')]:add(79,[board,word]);add(212,[[[c.lower() for c in row] for row in board],[word.lower(),'z']])
 good=[list(s) for s in ['53..7....','6..195...','.98....6.','8...6...3','4..8.3..1','7...2...6','.6....28.','...419..5','....8..79']];add(36,[good],True)
 bad=[x[:] for x in good];bad[0][1]='5';add(36,[bad],False)
 for points in [[[0,0]],[[0,0],[0,1]],[[1,1],[2,2],[3,3]],[[0,0],[1,1],[2,3]],[[1,0],[1,1],[1,2],[2,2]]]:add(149,[points])
 for k,w,p,c in [(1,0,[1],[0]),(2,0,[1,2,3],[0,1,1]),(3,0,[1,2],[1,2]),(2,10,[2,1],[0,0])]:add(502,[k,w,p,c])
 for cap in [1,2,3]:
  ops=['LRUCache'];args=[[cap]];expected=[None];d=collections.OrderedDict()
  for _ in range(50):
   key=R.randint(0,5)
   if R.random()<.6:
    val=R.randint(-5,5);ops.append('put');args.append([key,val]);expected.append(None)
    if key in d:del d[key]
    d[key]=val
    if len(d)>cap:d.popitem(last=False)
   else:
    ops.append('get');args.append([key]);expected.append(d.get(key,-1))
    if key in d:d.move_to_end(key)
  add(146,[ops,args],expected,'随机独立模型')
 for _ in range(10):
  ops=['MinStack'];args=[[]];expected=[None];a=[]
  for step in range(50):
   op=R.choice(['push','pop','top','getMin']) if a else 'push';ops.append(op)
   if op=='push':v=R.randint(-100,100);a.append(v);args.append([v]);expected.append(None)
   elif op=='pop':a.pop();args.append([]);expected.append(None)
   else:args.append([]);expected.append(a[-1] if op=='top' else min(a))
  add(155,[ops,args],expected,'随机独立模型')
 add(208,[['Trie','insert','search','search','startsWith','insert','search'],[[],['apple'],['apple'],['app'],['app'],['app'],['app']]],[None,None,True,False,True,None,True])
 add(211,[['WordDictionary','addWord','addWord','search','search','search','search'],[[],['bad'],['dad'],['pad'],['.ad'],['b..'],['...']]],[None,None,None,False,True,True,True])
 for _ in range(10):
  a=[R.randint(-50,50) for _ in range(30)];ops=['MedianFinder'];args=[[]];expect=[None];seen=[]
  for v in a:seen.append(v);seen.sort();ops+=['addNum','findMedian'];args.extend([[v],[]]);expect.extend([None,(seen[(len(seen)-1)//2]+seen[len(seen)//2])/2])
  add(295,[ops,args],expect,'随机独立模型')
 add(173,[['BSTIterator','hasNext','next','next','next','hasNext'],[[[2,1,3]],[],[],[],[],[]]],[None,True,1,2,3,False])
 add(380,[['RandomizedSet','insert','insert','getRandom','remove','getRandom','insert','remove','getRandom'],[[],[1],[2],[],[1],[],[2],[3],[]]],[None,True,True,'VALID_MEMBER',True,'VALID_MEMBER',False,False,'VALID_MEMBER'])
 # Prune arithmetic cases that violate the platform's 32-bit product guarantees.
 for id in [152,238]:
  SPECS[id]=[c for c in SPECS[id] if all(-2**31<=x<2**31 for x in (c.get('expected',[]) if id==238 else [c.get('expected',0)]))]
 return SPECS
