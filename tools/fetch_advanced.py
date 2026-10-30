import urllib.request,urllib.parse,json,pathlib,re,time,concurrent.futures
ROOT=pathlib.Path(__file__).resolve().parents[1];C=pathlib.Path('/private/tmp/algorithm-source-cache')
def get(u,data=None):
 for i in range(4):
  try:return urllib.request.urlopen(urllib.request.Request(u,data=json.dumps(data).encode() if data else None,headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0','Referer':'https://leetcode.cn/'}),timeout=35).read().decode()
  except Exception:
   if i==3:raise
   time.sleep(i+1)
slugs=re.findall(r'\[\d+-(.*?)\]',(C/'geekydevin-advanced.md').read_text())
def one(slug):
 d=json.loads(get('https://leetcode.cn/graphql/',{'query':'query($s:String!){question(titleSlug:$s){questionFrontendId title translatedTitle titleSlug difficulty content translatedContent codeSnippets{langSlug code} metaData sampleTestCase exampleTestcaseList isPaidOnly}}','variables':{'s':slug}}))['data']['question'];id=d['questionFrontendId'];dest=C/id;dest.mkdir(exist_ok=True);(dest/'detail.json').write_text(json.dumps(d,ensure_ascii=False));n=int(id);base=f'solution/{n//100*100:04d}-{n//100*100+99:04d}/{n:04d}.{d["title"]}/'
 for name in ['README.md','Solution.sql']:
  try:(dest/name).write_text(get('https://raw.githubusercontent.com/doocs/leetcode/main/'+urllib.parse.quote(base+name,safe='/')))
  except Exception as e:print('source note',id,name,str(e),flush=True)
 return {k:d[k] for k in ['questionFrontendId','title','translatedTitle','titleSlug','difficulty']}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:items=list(ex.map(one,slugs))
byid={x['questionFrontendId']:x for x in items};tree=json.loads((C/'advanced-tree.json').read_text());ordered=[byid[str(int(re.match(r'\d+-(\d+)-',x['path']).group(1)))] for x in sorted(tree['tree'],key=lambda x:x['path']) if re.match(r'\d+-\d+-',x['path'])]
assert len(ordered)==50 and len(byid)==50
bounds=[(5,'查询'),(11,'连接'),(20,'聚合'),(26,'排序与分组'),(32,'高级查询与连接'),(37,'子查询'),(46,'窗口与排名'),(50,'递归与连续区间')]
groups=[];start=0
for end,name in bounds:groups.append({'name':name,'questions':ordered[start:end]});start=end
plans=json.loads((ROOT/'catalog/plans.json').read_text());plans[3]['planSubGroups']=groups;plans[3]['sourceStatus']='公开题号索引交叉核对，官方接口未提供清单；分类为本工程教学分组，待官方复核';plans[3]['sources']=['https://github.com/leetlab11/Advanced-SQL-50','https://github.com/geekydevin/Leetcode-Advanced-SQL-50']
(ROOT/'catalog/plans.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2));q=json.loads((ROOT/'catalog/questions.json').read_text());q.update(byid);(ROOT/'catalog/questions.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print('ADVANCED DONE',len(items),'TOTAL',len(q),flush=True)
for name,url in [('CC-BY-SA-4.0.txt','https://raw.githubusercontent.com/doocs/leetcode/main/LICENSE')]:
 (ROOT/'licenses'/name).write_text(get(url))
