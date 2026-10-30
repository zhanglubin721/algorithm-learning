import pathlib,json,re,html,shutil
R=pathlib.Path(__file__).resolve().parents[1];C=(pathlib.Path(__file__).resolve().parents[1]/'.cache/source');briefs=dict(line.split('|',1) for line in (R/'tools/problem_briefs.txt').read_text().splitlines() if '|'in line)
ordered={1148,1280,620,1633,1729,1731,1978,626,1321,1667,1484,1873,1398,1112,1607,1407,1212,1445,603,1965,1549,1532,1831,1285,1412,1225}
for item in json.loads((R/'catalog/index.json').read_text()):
 q=R/item['path'];cfg=json.loads((q/'题目配置.json').read_text());sid=str(cfg['id']);d=json.loads((C/sid/'detail.json').read_text());sql=cfg['kind']=='sql';raw=d.get('translatedContent') or d.get('content') or ''
 if not raw:
  readme=(C/sid/'README.md').read_text();raw=readme.split('<!-- description:start -->')[-1].split('<!-- description:end -->')[0]
 cfg['ordered']=cfg['id']in ordered if sql else False;(q/'题目配置.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2))
 text=f'# LC{sid} {cfg["titleCn"]}\n\n{cfg["titleEn"]} · {cfg["difficulty"]} · {cfg["category"]}\n\n## 题意\n\n{briefs[sid]}\n\n'
 if sql:
  text+='## 表结构\n\n```sql\n'+';\n'.join(cfg['ddl'])+';\n```\n\n'
  text+='结果需要按题意排序。\n\n' if cfg['ordered'] else '未明确规定顺序的结果按无序行比较，但保留重复行数量。\n\n'
 else:
  template=(q/'模板/Solution.java.template').read_text();template=re.sub(r'/\*.*?\*/','',template,flags=re.S);text+='## 作答接口\n\n```java\n'+template.strip()+'\n```\n\n'
  meta=cfg['meta'];params=meta.get('params',[])
  if params:text+='输入依次为：'+', '.join(p['name']+'（'+p['type']+'）' for p in params)+'。\n\n'
  constraints=[]
  # Numeric bounds and input-shape constraints are factual data; do not copy the entire statement.
  for block in re.findall(r'<li>(.*?)</li>',raw,re.S):
   c=html.unescape(re.sub('<[^>]+>','',block)).strip()
   if any(x in c for x in ['<=','≤','长度','只包含','互不相同','升序','唯一','保证','范围']):constraints.append(c)
  if constraints:text+='## 约束要点\n\n'+''.join('- '+x+'\n' for x in constraints)+'\n'
 meta=cfg['meta'];examples=d.get('exampleTestcaseList') or ([d['sampleTestCase']] if d.get('sampleTestCase') else [])
 text+='## 示例输入\n\n'
 for i,e in enumerate(examples,1):
  if sql:
   try:
    data=json.loads(e)
    for table,headers in data['headers'].items():
     text+=f'示例{i} · {table}\n\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'
     for row in data['rows'][table]:text+='| '+' | '.join('NULL' if x is None else str(x) for x in row)+' |\n'
     text+='\n'
   except:text+='```json\n'+e+'\n```\n\n'
  else:text+=f'示例{i}\n\n```text\n'+e+'\n```\n\n'
 text+='## 本地使用\n\n运行入口中的Start.java，在控制台选择新一轮，然后编辑作答目录生成的副本。树用层序数组表示，链表用值数组表示；设计题使用操作名数组和参数数组。\n\n题目说明为本工程整理，来源：[力扣原题]('+cfg['source']+')。方法推导、复杂度和参考代码见[解题思路](题解/解题思路.md)。本地测试覆盖和验证情况见测试目录，不代表官方隐藏用例。\n'
 (q/'题目.md').write_text(text)
print('题意整理',len(briefs),'入口',len(json.loads((R/'catalog/index.json').read_text())))
