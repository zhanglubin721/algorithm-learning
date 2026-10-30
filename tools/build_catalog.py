from project_env import JAVA_BIN
import pathlib,json,re,html,hashlib,sys,subprocess,concurrent.futures,os,shutil
from test_specs import generate,SPECS
from extra_specs import extend
R=pathlib.Path(__file__).resolve().parents[1];C=(pathlib.Path(__file__).resolve().parents[1]/'.cache/source')
JAVA=JAVA_BIN
plans=json.loads((R/'catalog/plans.json').read_text());qs=json.loads((R/'catalog/questions.json').read_text());generate();extend()
D={'Easy':'简单','Medium':'中等','Hard':'困难','EASY':'简单','MEDIUM':'中等','HARD':'困难'}
def clean(s):return re.sub(r'[\\/:*?"<>|\s]+','_',s).strip('_')
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2))
def support(id):
 s='import java.util.*;\nclass ListNode { int val; ListNode next; ListNode(){} ListNode(int v){val=v;} ListNode(int v,ListNode n){val=v;next=n;} }\nclass TreeNode { int val; TreeNode left,right; TreeNode(){} TreeNode(int v){val=v;} TreeNode(int v,TreeNode l,TreeNode r){val=v;left=l;right=r;} }\nclass Pair<K,V>{ final K k;final V v;Pair(K k,V v){this.k=k;this.v=v;}K getKey(){return k;} V getValue(){return v;} public boolean equals(Object o){return o instanceof Pair<?,?> p&&Objects.equals(k,p.k)&&Objects.equals(v,p.v);} public int hashCode(){return Objects.hash(k,v);} }\n'
 if id==427:s+='class Node {boolean val,isLeaf;Node topLeft,topRight,bottomLeft,bottomRight;Node(){} Node(boolean v,boolean l){val=v;isLeaf=l;} Node(boolean v,boolean l,Node a,Node b,Node c,Node d){val=v;isLeaf=l;topLeft=a;topRight=b;bottomLeft=c;bottomRight=d;} }\n'
 elif id in [133,138,117]:s+='class Node {int val; Node next,random,left,right;List<Node> neighbors=new ArrayList<>();Node(){} Node(int v){val=v;}Node(int v,ArrayList<Node>ns){val=v;neighbors=ns;}Node(int v,List<Node>ns){val=v;neighbors=ns;}Node(int v,Node l,Node r,Node n){val=v;left=l;right=r;next=n;} }\n'
 return s
index=[];canonical={};roots=[]
for pi,plan in enumerate(plans):
 parent=['01-面试经典150','02-Hot100','03-SQL/01-SQL基础50','03-SQL/02-SQL进阶50'][pi]
 for gi,g in enumerate(plan['planSubGroups'],1):
  for q in g['questions']:
   id=int(q['questionFrontendId']);d=json.loads((C/str(id)/'detail.json').read_text());meta=json.loads(d['metaData']);sql=bool(meta.get('database'));diff=d['difficulty'];cn=d['translatedTitle'] or q.get('translatedTitle') or d['title'];namespace=f'p{pi+1}.lc{id:04d}';folder=f'LC{id:04d}_{clean(cn)}_{clean(d["title"])}_{D[diff]}-{diff}';rel=parent+'/'+f'{gi:02d}-{clean(g["name"])}'+'/'+folder;path=R/rel;path.mkdir(parents=True,exist_ok=True)
   for sub in ['题解','模板','测试','入口/src/main/java','作答/src/main/java']: (path/sub).mkdir(parents=True,exist_ok=True)
   cfg={'id':id,'titleCn':cn,'titleEn':d['title'],'slug':d['titleSlug'],'difficulty':diff,'kind':'sql' if sql else 'java','namespace':namespace,'plan':plan['slug'],'category':g['name'],'source':'https://leetcode.cn/problems/'+d['titleSlug']+'/','meta':meta,'importedAt':'2026-10-30','catalogStatus':plan.get('sourceStatus','官方公开题单')}
   if sql:cfg['ddl']=meta.get('mysql',[]);cfg['ordered']=bool(re.search(r'order.+by|排序|按.*顺序',html.unescape(re.sub('<[^>]+>',' ',d.get('translatedContent') or d.get('content') or '')),re.I))
   dump(path/'题目配置.json',cfg)
   raw=d.get('translatedContent') or d.get('content') or '';text=html.unescape(re.sub('<[^>]+>',' ',raw));text=re.sub(r'\s+',' ',text).strip();summary=text[:40]
   template=next((x['code'] for x in (d.get('codeSnippets') or []) if x['langSlug']==('mysql' if sql else 'java')),None)
   if template is None:template='-- 请在此编写查询\n' if sql else 'class Solution { /* 请参照题目契约实现 */ }'
   if not sql:
    template=re.sub(r'\{\s*\}', '{ throw new UnsupportedOperationException("TODO"); }',template)
    # comments from platform may include the node definition; actual support types are separate.
    template='import java.util.*;\nimport java.util.stream.*;\n'+template+'\n'
    (path/'模板/Support.java.template').write_text(support(id))
   (path/('模板/answer.sql.template' if sql else '模板/Solution.java.template')).write_text(template)
   entry=path/'入口/src/main/java/study/starts'/namespace.replace('.','/')/'Start.java';entry.parent.mkdir(parents=True,exist_ok=True);entry.write_text('package study.starts.'+namespace+';\npublic class Start { public static void main(String[] args) throws Exception { engine.Main.launch('+json.dumps(rel,ensure_ascii=False)+'); } }\n')
   roots += [rel+'/入口/src/main/java',rel+'/作答/src/main/java']
   readme=(C/str(id)/'README.md').read_text() if (C/str(id)/'README.md').exists() else ''
   sol=readme.split('<!-- solution:start -->',1)[-1] if '<!-- solution:start -->' in readme else ''
   sol=sol.split('<!-- solution:end -->')[0];sol=re.sub(r'```([^\n]*)\n(.*?)```',lambda m:m.group(0) if m.group(1).strip().lower() in ['java','sql','mysql','','text'] else '',sol,flags=re.S)
   sol=re.sub(r'(?m)^#{3,5}\s+(Python3?|C\+\+|C#|Go|Rust|JavaScript|TypeScript|Swift|Kotlin|Ruby|PHP|Scala|C|Elixir|Racket|Dart|Erlang|Cangjie)\s*$', '',sol);sol=re.sub(r'<!--[\s\S]*?-->','',sol);sol=re.sub(r'\n{4,}','\n\n',sol)
   source='https://github.com/doocs/leetcode/tree/main/'+f'solution/{id//100*100:04d}-{id//100*100+99:04d}/{id:04d}.'+d['title'].replace(' ','%20')
   prefix=f'# LC{id} {cn} 解题思路\n\n本文件为开源参考内容的节选与格式整理，不是力扣官方题解。来源：[doocs/leetcode]({source})，作者：Doocs及贡献者，许可：CC BY-SA 4.0。修改：保留中文分析及Java/SQL代码，移除其他语言；许可证见工程licenses目录。\n\n'
   (path/'题解/解题思路.md').write_text(prefix+sol)
   (path/'题解/分级提示.md').write_text(f'# LC{id} 分级提示\n\n先写清输入规模、允许修改的对象和结果判定方式。\n\n需要进一步帮助时，打开[解题思路](解题思路.md)，先阅读第一种方法的思考部分，再看代码。\n')
   ref_file=C/str(id)/('Solution.sql' if sql else 'Solution.java');ref=ref_file.read_text() if ref_file.exists() else ''
   if not ref:
    codes=re.findall(r'```(?:mysql|sql)\n(.*?)```',readme,re.S);ref=codes[0] if codes else ''
   (path/'题解'/('参考答案.sql' if sql else 'Solution.java.reference')).write_text(ref)
   examples=d.get('exampleTestcaseList') or ([d['sampleTestCase']] if d.get('sampleTestCase') else [])
   body=f'# LC{id} {cn}\n\n英文名：{d["title"]}  \n难度：{D[diff]} / {diff}  \n题单分类：{g["name"]}  \n[原题]({cfg["source"]})\n\n'
   if summary:body+='## 来源摘要\n\n> '+summary+'…\n\n'
   body+='## 作答契约\n\n'
   if sql:body+='在MySQL 8中编写对应查询。建表契约：\n\n```sql\n'+';\n'.join(cfg['ddl'])+';\n```\n\n'
   else:body+='方法与类型以模板为准。系统设计题按操作序列调用；原地修改题会校验参数变化。\n\n```json\n'+json.dumps(meta,ensure_ascii=False,indent=2)+'\n```\n\n'
   body+='## 公开示例输入\n\n'+''.join('```'+('json' if sql else 'text')+'\n'+e+'\n```\n\n' for e in examples)
   body+='## 使用方法\n\n运行入口中的Start.java创建作答副本。题意的详细推导见题解目录，作答前可先只阅读本页与模板。这里保存摘要、接口与公开样例；完整原题以来源链接为准。\n\n本地测试含额外构造样例，不等于平台隐藏测试。每轮结束可导出AI复核材料。\n'
   (path/'题目.md').write_text(body)
   index.append({'id':id,'path':rel,'namespace':namespace,'kind':cfg['kind'],'plan':plan['slug'],'class':'study.starts.'+namespace+'.Start'})
   if id not in canonical:canonical[id]=path
# Persist canonical index so tests can be built once per distinct problem.
dump(R/'catalog/index.json',index);dump(R/'catalog/canonical.json',{str(k):str(v.relative_to(R)) for k,v in canonical.items()});dump(R/'catalog/source-roots.json',roots)
for id,path in canonical.items():
 cfg=json.loads((path/'题目配置.json').read_text());d=json.loads((C/str(id)/'detail.json').read_text())
 if cfg['kind']=='java':
  cases=[]
  for i,example in enumerate(d.get('exampleTestcaseList') or []):
   try:args=[json.loads(x) for x in example.strip().splitlines()];cases.append({'name':f'公开示例-{i+1}','args':args,'source':'官方公开输入','oracle':'reference-crosscheck'})
   except Exception as e: print('example parse note',id,e)
  cases+=SPECS[id];unique={}
  for c in cases:unique[json.dumps(c['args'],sort_keys=True)]=c
  dump(path/'测试/cases.json',list(unique.values()))
 else:
  cases=[]
  for i,example in enumerate(d.get('exampleTestcaseList') or ([d['sampleTestCase']] if d.get('sampleTestCase') else [])):
   try:
    data=json.loads(example)
    if 'headers' in data:cases.append({'name':f'公开数据-{i+1}','data':data,'oracle':'reference-plus-example'})
   except:pass
  if not cases:
   # Paid statements can omit sample data; preserve explicit status instead of inventing a passed fixture.
   dump(path/'测试/待补数据.json',{'reason':'公开接口未提供示例数据，需从合法参考中构造并校验'})
  dump(path/'测试/sql-cases.json',cases)
print('CATALOG',len(index),'unique',len(canonical),'cases',sum(len(json.loads((v/'测试/cases.json').read_text())) for v in canonical.values() if (v/'测试/cases.json').exists()),flush=True)
