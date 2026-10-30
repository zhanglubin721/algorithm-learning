import json,pathlib,re,html,copy,random,collections,decimal,datetime
R=pathlib.Path(__file__).resolve().parents[1];C=pathlib.Path('/private/tmp/algorithm-source-cache');rng=random.Random(20261030)
def normalize(v):
 if v is None:return None
 if isinstance(v,(int,float,decimal.Decimal)):return format(decimal.Decimal(str(v)).normalize(),'f')
 return str(v)
def result(cols,rows):return [cols,[[normalize(x) for x in row] for row in rows]]
def records(data,table):
 table=next(k for k in data['headers'] if k.lower()==table.lower());return [dict(zip([x.lower() for x in data['headers'][table]],r)) for r in data['rows'][table]]
def n(x):return int(x)
def oracle(id,d):
 def rows(t):return records(d,t)
 def out(cs,rs):return result(cs.split(','),rs)
 if id==1757:return out('product_id',[[r['product_id']] for r in rows('Products') if r['low_fats']=='Y' and r['recyclable']=='Y'])
 if id==584:return out('name',[[r['name']] for r in rows('Customer') if r['referee_id'] is None or n(r['referee_id'])!=2])
 if id==595:return out('name,population,area',[[r['name'],r['population'],r['area']] for r in rows('World') if n(r['area'])>=3000000 or n(r['population'])>=25000000])
 if id==1148:return out('id',[[x] for x in sorted({n(r['author_id']) for r in rows('Views') if n(r['author_id'])==n(r['viewer_id'])})])
 if id==1683:return out('tweet_id',[[r['tweet_id']] for r in rows('Tweets') if len(r['content'])>15])
 if id==1378:
  ids={n(r['id']):r['unique_id'] for r in rows('EmployeeUNI')};return out('unique_id,name',[[ids.get(n(r['id'])),r['name']] for r in rows('Employees')])
 if id==1068:
  names={n(r['product_id']):r['product_name'] for r in rows('Product')};return out('product_name,year,price',[[names[n(r['product_id'])],r['year'],r['price']] for r in rows('Sales')])
 if id==1581:
  yes={n(r['visit_id']) for r in rows('Transactions')};c=collections.Counter(n(r['customer_id']) for r in rows('Visits') if n(r['visit_id']) not in yes);return out('customer_id,count_no_trans',list(c.items()))
 if id==197:
  a=rows('Weather');temps={datetime.date.fromisoformat(r['recorddate']):n(r['temperature']) for r in a};return out('id',[[r['id']] for r in a if temps.get(datetime.date.fromisoformat(r['recorddate'])-datetime.timedelta(days=1),10**9)<n(r['temperature'])])
 if id==577:
  bonus={n(r['empid']):r['bonus'] for r in rows('Bonus')};return out('name,bonus',[[r['name'],bonus.get(n(r['empid']))] for r in rows('Employee') if bonus.get(n(r['empid'])) is None or n(bonus[n(r['empid'])])<1000])
 if id==1280:
  c=collections.Counter((n(r['student_id']),r['subject_name']) for r in rows('Examinations'));return out('student_id,student_name,subject_name,attended_exams',[[s['student_id'],s['student_name'],sub['subject_name'],c[n(s['student_id']),sub['subject_name']]] for s in sorted(rows('Students'),key=lambda r:n(r['student_id'])) for sub in sorted(rows('Subjects'),key=lambda r:r['subject_name'])])
 if id==570:
  c=collections.Counter(n(r['managerid']) for r in rows('Employee') if r['managerid'] is not None);return out('name',[[r['name']] for r in rows('Employee') if c[n(r['id'])]>=5])
 if id==620:return out('id,movie,description,rating',[[r[k] for k in ['id','movie','description','rating']] for r in sorted(rows('cinema'),key=lambda r:-float(r['rating'])) if n(r['id'])%2 and r['description']!='boring'])
 if id==2356:
  groups=collections.defaultdict(set)
  for r in rows('Teacher'):groups[n(r['teacher_id'])].add(n(r['subject_id']))
  return out('teacher_id,cnt',[[k,len(v)] for k,v in groups.items()])
 if id==596:
  groups=collections.defaultdict(set)
  for r in rows('Courses'):groups[r['class']].add(r['student'])
  return out('class',[[k] for k,v in groups.items() if len(v)>=5])
 if id==1729:
  c=collections.Counter(n(r['user_id']) for r in rows('Followers'));return out('user_id,followers_count',sorted(c.items()))
 if id==619:
  c=collections.Counter(n(r['num']) for r in rows('MyNumbers'));return out('num',[[max((k for k,v in c.items() if v==1),default=None)]])
 if id==1045:
  products={n(r['product_key']) for r in rows('Product')};g=collections.defaultdict(set)
  for r in rows('Customer'):g[n(r['customer_id'])].add(n(r['product_key']))
  return out('customer_id',[[k] for k,v in g.items() if products<=v])
 if id==610:return out('x,y,z,triangle',[[r['x'],r['y'],r['z'],'Yes' if sum(n(r[k]) for k in ['x','y','z'])>2*max(n(r[k]) for k in ['x','y','z']) else 'No'] for r in rows('Triangle')])
 if id==1907:
  a=[n(r['income']) for r in rows('Accounts')];return out('category,accounts_count',[['Low Salary',sum(x<20000 for x in a)],['Average Salary',sum(20000<=x<=50000 for x in a)],['High Salary',sum(x>50000 for x in a)]])
 if id==1978:
  a=rows('Employees');ids={n(r['employee_id']) for r in a};return out('employee_id',[[n(r['employee_id'])] for r in sorted(a,key=lambda r:n(r['employee_id'])) if n(r['salary'])<30000 and r['manager_id'] is not None and n(r['manager_id']) not in ids])
 if id==626:
  a=sorted(rows('Seat'),key=lambda r:n(r['id']));return out('id,student',[[r['id'],a[i+1 if i%2==0 and i+1<len(a) else i-1 if i%2 else i]['student']] for i,r in enumerate(a)])
 if id==1667:return out('user_id,name',[[r['user_id'],r['name'][:1].upper()+r['name'][1:].lower()] for r in sorted(rows('Users'),key=lambda r:n(r['user_id']))])
 if id==1527:return out('patient_id,patient_name,conditions',[[r['patient_id'],r['patient_name'],r['conditions']] for r in rows('Patients') if any(t.startswith('DIAB1') for t in r['conditions'].split())])
 if id==196:
  seen={}
  for r in rows('Person'):
   email=r['email'].lower()
   if email not in seen or n(r['id'])<n(seen[email]['id']):seen[email]=r
  return out('id,email',[[r['id'],r['email']] for r in seen.values()])
 if id==176:
  a=sorted({n(r['salary']) for r in rows('Employee')},reverse=True);return out('SecondHighestSalary',[[a[1] if len(a)>1 else None]])
 if id==1517:return out('user_id,name,mail',[[r['user_id'],r['name'],r['mail']] for r in rows('Users') if re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_.-]*@leetcode\.com',r['mail'])])
 if id==1821:return out('customer_id',[[r['customer_id']] for r in rows('Customers') if n(r['year'])==2021 and n(r['revenue'])>0])
 if id==183:
  ids={n(r['customerid']) for r in rows('Orders')};return out('Customers',[[r['name']] for r in rows('Customers') if n(r['id']) not in ids])
 if id==1873:return out('employee_id,bonus',[[r['employee_id'],r['salary'] if n(r['employee_id'])%2 and not r['name'].startswith('M') else 0] for r in sorted(rows('Employees'),key=lambda r:n(r['employee_id']))])
 if id==175:
  g=collections.defaultdict(list)
  for r in rows('Address'):g[n(r['personid'])].append(r)
  return out('firstName,lastName,city,state',[[r['firstname'],r['lastname'],a.get('city'),a.get('state')] for r in rows('Person') for a in g.get(n(r['personid']),[{}])])
 if id in [511,512]:
  g={}
  for r in rows('Activity'):
   k=n(r['player_id'])
   if k not in g or r['event_date']<g[k]['event_date']:g[k]=r
  return out('player_id,'+('first_login' if id==511 else 'device_id'),[[k,r['event_date'] if id==511 else r['device_id']] for k,r in g.items()])
 if id==182:
  c=collections.Counter(r['email'] for r in rows('Person'));return out('Email',[[k] for k,v in c.items() if v>1])
 if id==1050:
  c=collections.Counter((n(r['actor_id']),n(r['director_id'])) for r in rows('ActorDirector'));return out('actor_id,director_id',[list(k) for k,v in c.items() if v>=3])
 if id==603:
  free={n(r['seat_id']) for r in rows('Cinema') if n(r['free'])};return out('seat_id',[[x] for x in sorted(free) if x-1 in free or x+1 in free])
 if id==1795:return out('product_id,store,price',[[r['product_id'],k,r[k]] for r in rows('Products') for k in ['store1','store2','store3'] if r[k] is not None])
 if id==613:
  a=sorted(n(r['x']) for r in rows('Point'));return out('shortest',[[min((a[i]-a[i-1] for i in range(1,len(a))),default=None)]])
 if id==1965:
  a={n(r['employee_id']) for r in rows('Employees')};b={n(r['employee_id']) for r in rows('Salaries')};return out('employee_id',[[x] for x in sorted(a^b)])
 if id==1303:
  a=rows('Employee');c=collections.Counter(n(r['team_id']) for r in a);return out('employee_id,team_size',[[r['employee_id'],c[n(r['team_id'])]] for r in a])
 if id==1767:
  done={(n(r['task_id']),n(r['subtask_id'])) for r in rows('Executed')};return out('task_id,subtask_id',[[r['task_id'],i] for r in rows('Tasks') for i in range(1,n(r['subtasks_count'])+1) if (n(r['task_id']),i) not in done])
 return None

def parse_output(readme):
 text=html.unescape(re.sub('<[^>]+>','',readme.split('<!-- description:end -->')[0]));parts=re.split(r'输出\s*[:：]|Output\s*:',text)
 outs=[]
 for p in parts[1:]:
  lines=p.splitlines();rows=[];started=False
  for line in lines:
   line=line.strip()
   if line.startswith('|'):
    started=True;rows.append([x.strip() for x in line.strip('|').split('|')])
   elif started and not line.startswith('+') and line:break
  if rows:
   cs=rows.pop(0);data=[]
   for row in rows:
    out=[]
    for x in row:
     if x.lower()=='null':out.append(None)
     elif re.fullmatch(r'-?\d+(\.\d+)?',x):out.append(format(decimal.Decimal(x).normalize(),'f'))
     else:out.append(x)
    data.append(out)
   outs.append([cs,data])
 return outs

def custom(id,base):
 # Carefully constructed threshold, NULL and join cases for the most error-prone semantics.
 fixtures={
 1757:{'Products':[[1,'Y','Y'],[2,'Y','N'],[3,'N','Y'],[4,'N','N']]},
 584:{'Customer':[[1,'A',None],[2,'B',2],[3,'C',1],[4,'D',3]]},
 595:{'World':[['A','X',2999999,24999999,1],['B','X',3000000,1,1],['C','X',1,25000000,1],['D','X',3000001,25000001,1]]},
 1148:{'Views':[[1,1,1,'2020-01-01'],[1,1,1,'2020-01-01'],[2,2,3,'2020-01-01'],[3,4,4,'2020-01-01']]},
 1683:{'Tweets':[[1,'a'*14],[2,'b'*15],[3,'c'*16],[4,'d'*50]]},
 1378:{'Employees':[[1,'A'],[2,'B'],[3,'C']],'EmployeeUNI':[[2,200],[3,300]]},
 197:{'Weather':[[1,'2020-02-28',10],[2,'2020-02-29',11],[3,'2020-03-01',11],[4,'2020-03-03',30],[5,'2020-03-04',20]]},
 619:{'MyNumbers':[[1],[1],[2],[2]]},176:{'Employee':[[1,100],[2,100]]},
 1907:{'Accounts':[[1,19999],[2,20000],[3,50000],[4,50001]]},
 610:{'Triangle':[[1,2,3],[2,2,3],[1,1,1],[10,2,2]]},
 1527:{'Patients':[[1,'A','DIAB1'],[2,'B','XDIAB1'],[3,'C','ACNE DIAB100'],[4,'D',''],[5,'E','DIAB2']]},
 1517:{'Users':[[1,'A','a@leetcode.com'],[2,'B','1a@leetcode.com'],[3,'C','a@leetcodeXcom'],[4,'D','a-b_c.d@leetcode.com'],[5,'E','.a@leetcode.com']]},
 196:{'Person':[[7,'a@x.com'],[2,'a@x.com'],[9,'b@x.com'],[1,'b@x.com']]},
 1821:{'Customers':[[1,2021,0],[2,2021,-1],[3,2021,1],[4,2020,100]]},
 603:{'Cinema':[[1,1],[2,0],[3,1],[4,1],[5,1],[6,0],[7,1]]},
 1795:{'Products':[[1,0,None,5],[2,None,None,None],[3,8,8,8]]},
 175:{'Person':[[1,'A','One'],[2,'B','Two']],'Address':[[1,2,'X','Y']]},
 1965:{'Employees':[[1,'A'],[2,'B']],'Salaries':[[2,200],[3,300]]},
 1767:{'Tasks':[[1,3],[2,1]],'Executed':[[1,1],[1,3]]}
 }
 if id not in fixtures:return []
 d=copy.deepcopy(base)
 for t,rs in fixtures[id].items():
  key=next(k for k in d['rows'] if k.lower()==t.lower());d['rows'][key]=rs
 return [d]

if __name__=='__main__':
 idx=json.loads((R/'catalog/canonical.json').read_text());stats={}
 for sid,rel in idx.items():
  q=R/rel;cfg=json.loads((q/'题目配置.json').read_text());id=int(sid)
  if cfg['kind']!='sql':continue
  cases=json.loads((q/'测试/sql-cases.json').read_text());readme=(C/sid/'README.md').read_text();outs=parse_output(readme)
  for i,c in enumerate(cases):
   got=oracle(id,c['data']);c['expected']=got if got is not None else outs[i] if i<len(outs) else None;c['oracle']='independent-python' if got is not None else 'published-example';
   if c['expected']is None:del c['expected'];c['oracle']='runtime-reference'
  if cases:
   base=cases[0]['data'];more=custom(id,base)
   # Record order is deliberately scrambled; SQL output must obey its own ORDER BY.
   for seed in range(3):
    data=copy.deepcopy(base)
    for rs in data['rows'].values():random.Random(seed+17).shuffle(rs)
    more.append(data)
   # Remove fact records only for tables whose domain permits arbitrary event subsets.
   SAFE={1148:'Views',1581:'Transactions',1280:'Examinations',1934:'Confirmations',1633:'Register',1211:'Queries',1193:'Transactions',2356:'Teacher',596:'Courses',1729:'Followers',619:'MyNumbers',1045:'Customer',1484:'Activities',1327:'Orders',183:'Orders',1398:'Orders',1607:'Orders',1407:'Rides',607:'Orders',1890:'Logins',586:'orders',1587:'Transactions',182:'Person',1050:'ActorDirector',1693:'DailySales',1495:'TVProgram',1699:'Calls',1795:'Products',1965:'Salaries',1264:'Likes',1783:'Championships',1747:'LogInfo',1549:'Orders',1532:'Orders',1831:'Transactions',1077:'Project',1596:'Orders',1767:'Executed'}
   if id in SAFE:
    t=next(k for k in base['rows'] if k.lower()==SAFE[id].lower())
    for frac in [0,0.3,0.7]:
     data=copy.deepcopy(base);data['rows'][t]=data['rows'][t][:int(len(data['rows'][t])*frac)];more.append(data)
   for j,data in enumerate(more):
    exp=oracle(id,data);c={'name':f'构造边界-{j+1}','data':data,'oracle':'independent-python' if exp is not None else 'runtime-reference'}
    if exp is not None:c['expected']=exp
    elif data==base and cases[0].get('expected')is not None:c['expected']=cases[0]['expected'];c['oracle']='published-example'
    cases.append(c)
  unique={json.dumps(c['data'],sort_keys=True):c for c in cases};cases=list(unique.values());(q/'测试/sql-cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2));stats[sid]={'cases':len(cases),'fixedExpected':sum('expected'in c for c in cases),'mysqlExecuted':False}
 (R/'progress/SQL测试准备.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2));print('SQL fixtures',len(stats),sum(v['cases'] for v in stats.values()),'fixed',sum(v['fixedExpected'] for v in stats.values()))
