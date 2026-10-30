#!/usr/bin/env python3
"""Read public metadata and licensed reference sources. Never uses account cookies."""
import urllib.request,urllib.error,json,time,concurrent.futures,pathlib,urllib.parse,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
CACHE=(pathlib.Path(__file__).resolve().parents[1]/'.cache/source');CACHE.mkdir(exist_ok=True)
PLANS=['top-interview-150','top-100-liked','sql-free-50','sql-premium-50']
def get(url,data=None):
 for n in range(4):
  try:
   req=urllib.request.Request(url,data=json.dumps(data).encode() if data else None,headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0','Referer':'https://leetcode.cn/'})
   return urllib.request.urlopen(req,timeout=35).read().decode()
  except urllib.error.HTTPError as e:
   if e.code in (400,403,404):raise
   time.sleep(1+n)
  except Exception:
   if n==3:raise
   time.sleep(1+n)
def gql(q,vars={}):
 d=json.loads(get('https://leetcode.cn/graphql/',{'query':q,'variables':vars}))
 if d.get('errors'):raise RuntimeError(d['errors'])
 return d['data']
allq={};plans=[]
for slug in PLANS:
 path=CACHE/(slug+'.json')
 if path.exists():d=json.loads(path.read_text())
 else:
  d=gql('query($slug:String!){studyPlanV2Detail(planSlug:$slug){name slug planSubGroups{name questions{questionFrontendId title titleSlug translatedTitle difficulty}}}}',{'slug':slug})['studyPlanV2Detail'];path.write_text(json.dumps(d,ensure_ascii=False))
 plans.append(d)
 for group in d['planSubGroups']:
  for q in group['questions']:allq[q['questionFrontendId']]=q
 print(slug,sum(len(g['questions']) for g in d['planSubGroups']),flush=True)
(ROOT/'catalog/plans.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2))
(ROOT/'catalog/questions.json').write_text(json.dumps(allq,ensure_ascii=False,indent=2))
def one(item):
 id,q=item; dest=CACHE/id;dest.mkdir(exist_ok=True);errors=[]
 try:
  f=dest/'detail.json'
  if not f.exists():
   d=gql('query($slug:String!){question(titleSlug:$slug){questionFrontendId title translatedTitle titleSlug difficulty content translatedContent codeSnippets{langSlug code} metaData sampleTestCase exampleTestcaseList isPaidOnly}}',{'slug':q['titleSlug']})['question'];f.write_text(json.dumps(d,ensure_ascii=False))
 except Exception as e: errors.append('detail:'+str(e))
 n=int(id);base=f'solution/{n//100*100:04d}-{n//100*100+99:04d}/{n:04d}.{q["title"]}/'
 for name in ['README.md','Solution.java','Solution.sql']:
  is_sql=any(q['questionFrontendId']==x['questionFrontendId'] for p in plans[2:] for g in p['planSubGroups'] for x in g['questions'])
  if name=='Solution.sql' and not is_sql or name=='Solution.java' and is_sql:continue
  f=dest/name
  if f.exists():continue
  try:f.write_text(get('https://raw.githubusercontent.com/doocs/leetcode/main/'+urllib.parse.quote(base+name,safe='/')))
  except Exception as e:errors.append(name+':'+str(e))
 return id,errors
errors={}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for i,(id,err) in enumerate(ex.map(one,allq.items()),1):
  if err:errors[id]=err
  if i%20==0:print('details',i,'/',len(allq),'with notes',len(errors),flush=True)
(ROOT/'catalog/import-notes.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2))
print('DONE',len(allq), 'notes',len(errors),flush=True)
