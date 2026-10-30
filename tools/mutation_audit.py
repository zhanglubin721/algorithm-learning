import pathlib,json,re,subprocess,concurrent.futures,hashlib
R=pathlib.Path(__file__).resolve().parents[1];J='/Users/a58/Library/Java/JavaVirtualMachines/graalvm-jdk-21.0.7/Contents/Home/bin/';index=json.loads((R/'catalog/canonical.json').read_text())
def mutants(src):
 out=[]
 # Replace one externally callable method with a type-correct constant result.
 for m in re.finditer(r'public\s+([\w<>\[\], ?]+?)\s+(\w+)\s*\([^)]*\)\s*\{',src):
  typ=m.group(1).strip();depth=1;j=m.end()
  while j<len(src) and depth:
   depth+=(src[j]=='{')-(src[j]=='}');j+=1
  val={'void':'','int':'return 0;','long':'return 0L;','double':'return 0.0;','float':'return 0f;','boolean':'return false;','char':"return 'a';"}.get(typ,'return null;')
  out.append(('constant-result',src[:m.end()]+val+src[j-1:]));break
 # Change a loop/if boundary, retaining a well-formed Java expression.
 for m in re.finditer(r'\b(?:if|for|while)\s*\([^\n]*',src):
  part=m.group();op=re.search(r'(?<![<>=!])(?:<=|>=|<|>)(?![<>=])',part)
  if op:
   old=op.group();new={'<':'<=','<=':'<','>':'>=','>=':'>'}[old];at=m.start()+op.start();out.append(('boundary-change',src[:at]+new+src[at+len(old):]));break
 return out

def audit(item):
 sid,rel=item;q=R/rel;cfg=json.loads((q/'题目配置.json').read_text())
 if cfg['kind']=='sql':return sid,None
 ref=(q/'题解/Solution.java.reference').read_text();results=[]
 for label,code in mutants(ref):
  w=R/'.cache/mutations'/sid/label;w.mkdir(parents=True,exist_ok=True);pkg='mutant.p'+sid;src=w/'Solution.java';src.write_text('package '+pkg+';\nimport java.util.*;\nimport java.util.stream.*;\nimport java.util.concurrent.*;\nimport java.util.concurrent.atomic.*;\n'+code);(w/'Support.java').write_text('package '+pkg+';\n'+(q/'模板/Support.java.template').read_text())
  comp=subprocess.run([J+'javac','-encoding','UTF-8','-d',str(w),str(src),str(w/'Support.java')],capture_output=True,text=True)
  if comp.returncode:results.append({'mutation':label,'status':'INVALID_MUTANT'});continue
  out=w/'results.json';out.unlink(missing_ok=True)
  try:p=subprocess.run([J+'java','-Xmx128m','-Xss4m','-cp',str(R/'.cache/engine'),'engine.Worker',str(w),str(q/'题目配置.json'),str(q/'测试/cases.json'),str(out),pkg],capture_output=True,text=True,timeout=12)
  except subprocess.TimeoutExpired:results.append({'mutation':label,'status':'KILLED_TIMEOUT'});continue
  res=json.loads(out.read_text()) if out.exists() else [];fail=next((x for x in res if not x.get('passed')),None);killed=p.returncode!=0 or fail is not None;results.append({'mutation':label,'status':'KILLED' if killed else 'SURVIVED_REVIEW_REQUIRED','counterexample':fail})
 report={'mutations':results,'note':'错误解检测只是有限证据；幸存变异可能等价，也可能提示缺口，不能视为证明。'};(q/'测试/变异测试报告.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));return sid,report
report={}
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
 for k,(sid,res) in enumerate(pool.map(audit,index.items()),1):
  if res:report[sid]=res
  if k%30==0:print('mutations',k,flush=True)
(R/'progress/变异测试总报告.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('DONE mutations',len(report),flush=True)
