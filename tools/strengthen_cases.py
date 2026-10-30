import pathlib,json,random,collections,itertools,copy
R=pathlib.Path(__file__).resolve().parents[1];idx=json.loads((R/'catalog/canonical.json').read_text());rng=random.Random(20261101);extra=collections.defaultdict(list)
def add(i,args,exp=None,known=False):
 c={'name':f'强化-{len(extra[i])+1:03d}','args':args,'oracle':'independent-python' if known else 'reference-crosscheck','source':'工程定向构造'}
 if known:c['expected']=exp
 extra[i].append(c)
def tree_array(t):
 if not t:return []
 out=[];q=collections.deque([t])
 while q:
  x=q.popleft();out.append(x[0] if x else None)
  if x:q.extend(x[1:])
 while out and out[-1]is None:out.pop()
 return out
def ins(t,x):
 if t is None:return [x,None,None]
 t[1 if x<t[0] else 2]=ins(t[1 if x<t[0] else 2],x);return t
def traversals(t):
 if not t:return [],[],[]
 a,b,c=traversals(t[1]);d,e,f=traversals(t[2]);return [t[0]]+a+d,b+[t[0]]+e,c+f+[t[0]]
for n in range(1,26):
 vals=rng.sample(range(-100,100),n);t=None
 for v in vals:t=ins(t,v)
 arr=tree_array(t);pre,ino,post=traversals(t)
 add(105,[pre,ino],arr,True);add(106,[ino,post],arr,True)
 for id in [104,226,101,199,637,102,103,543,114,117,124]:add(id,[arr])
 add(94,[arr],ino,True);add(98,[arr],True,True);add(100,[arr,arr],True,True)
 if n>=2:
  add(530,[arr],min(b-a for a,b in zip(ino,ino[1:])),True);add(236,[arr,vals[0],vals[-1]],vals[0],True)
  adj=[[]for _ in range(n)]
  for j in range(1,n):k=rng.randrange(j);adj[j].append(k+1);adj[k].append(j+1)
  add(133,[adj])
 add(138,[[[rng.randint(-20,20),rng.choice([None]+list(range(n)))]for _ in range(n)]])
 ops=['BSTIterator'];args=[[arr]];exp=[None]
 for v in ino:ops+=['hasNext','next'];args.extend([[],[]]);exp.extend([True,v])
 ops+=['hasNext'];args.append([]);exp.append(False);add(173,[ops,args],exp,True)
for _ in range(30):
 words=set();ops=['Trie'];args=[[]];exp=[None];dops=['WordDictionary'];dargs=[[]];dexp=[None]
 for k in range(80):
  w=''.join(rng.choice('abcd')for _ in range(rng.randint(1,7)))
  if k%3==0:words.add(w);ops.append('insert');args.append([w]);exp.append(None);dops.append('addWord');dargs.append([w]);dexp.append(None)
  else:
   op=rng.choice(['search','startsWith']);ops.append(op);args.append([w]);exp.append(w in words if op=='search' else any(x.startswith(w)for x in words));pattern=''.join('.' if rng.random()<.4 else x for x in w);dops.append('search');dargs.append([pattern]);dexp.append(any(len(x)==len(pattern)and all(a=='.'or a==b for a,b in zip(pattern,x))for x in words))
 add(208,[ops,args],exp,True);add(211,[dops,dargs],dexp,True)
for _ in range(30):
 live=set();ops=['RandomizedSet'];args=[[]];exp=[None]
 for k in range(100):
  op=rng.choice(['insert','remove','getRandom']) if live else 'insert';v=rng.randint(-10,10);ops.append(op)
  if op=='getRandom':args.append([]);exp.append('VALID_MEMBER')
  elif op=='insert':args.append([v]);exp.append(v not in live);live.add(v)
  else:args.append([v]);exp.append(v in live);live.discard(v)
 add(380,[ops,args],exp,True)
for strs in [['a','ab'],['','a'],['ab','abcd'],['abc','abcde','abcd']]:
 pref=strs[0]
 while any(not s.startswith(pref)for s in strs):pref=pref[:-1]
 add(14,[strs],pref,True)
for n in range(2,10):
 for _ in range(5):
  edges=[[j,i]for i in range(n)for j in range(i+1,n)if rng.random()<.2];add(207,[n,edges],True,True);add(210,[n,edges]);cycle=[[i,(i+1)%n]for i in range(n)];add(207,[n,cycle],False,True);add(210,[n,cycle],[],True)
for i,new in extra.items():
 p=R/idx[str(i)]/'测试/cases.json';old=json.loads(p.read_text());keys={json.dumps(c['args'],sort_keys=True)for c in old};old.extend(c for c in new if json.dumps(c['args'],sort_keys=True)not in keys);p.write_text(json.dumps(old,ensure_ascii=False,indent=2))
print('强化新增',sum(map(len,extra.values())),'题目',len(extra))
