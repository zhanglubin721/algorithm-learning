from project_env import JAVA_BIN
import pathlib,json,subprocess,concurrent.futures,time,re,sys,hashlib
R=pathlib.Path(__file__).resolve().parents[1];J=JAVA_BIN;idx=json.loads((R/'catalog/canonical.json').read_text())

def verify(item):
 id,rel=item;q=R/rel;cfg=json.loads((q/'题目配置.json').read_text())
 if cfg['kind']=='sql':return id,{'status':'MYSQL_PENDING','cases':len(json.loads((q/'测试/sql-cases.json').read_text()))}
 w=R/'.cache/reference'/id;w.mkdir(parents=True,exist_ok=True);pkg='reference.p'+id;src=w/'Solution.java';src.write_text('package '+pkg+';\nimport java.util.*;\nimport java.util.stream.*;\nimport java.util.concurrent.*;\nimport java.util.concurrent.atomic.*;\n'+(q/'题解/Solution.java.reference').read_text());(w/'Support.java').write_text('package '+pkg+';\n'+(q/'模板/Support.java.template').read_text())
 proc=subprocess.run([J+'javac','-encoding','UTF-8','-g','-d',str(w),str(src),str(w/'Support.java')],capture_output=True,text=True)
 if proc.returncode:return id,{'status':'REFERENCE_COMPILE_ERROR','error':proc.stderr}
 out=w/'results.json'
 try:run=subprocess.run([J+'java','-Xmx256m','-Xss4m','-cp',str(R/'.cache/engine'),'engine.Worker',str(w),str(q/'题目配置.json'),str(q/'测试/cases.json'),str(out),pkg],capture_output=True,text=True,timeout=40)
 except subprocess.TimeoutExpired:return id,{'status':'REFERENCE_TIMEOUT'}
 if not out.exists():return id,{'status':'WORKER_ERROR','error':run.stderr}
 res=json.loads(out.read_text());cases=json.loads((q/'测试/cases.json').read_text());bad=[];independent=0
 for c,x in zip(cases,res):
  if 'error'in x:bad.append({'case':c,'result':x});continue
  if 'expected'in c:
   independent+=int(c.get("oracle")=="independent-python")
   if not x['passed']:bad.append({'case':c,'result':x})
  else:c['expected']=x['actual']
 (q/'测试/cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2))
 report={'status':'REFERENCE_VERIFIED' if not bad and len(res)==len(cases) else 'NEEDS_FIX','cases':len(cases),'independentOracleCases':independent,'failures':bad,'referenceSha256':hashlib.sha256((q/'题解/Solution.java.reference').read_bytes()).hexdigest()}
 (q/'测试/质量报告.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));return id,report
report={}
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as ex:
 for n,(id,status) in enumerate(ex.map(verify,idx.items()),1):
  report[id]=status
  if status['status']not in ['REFERENCE_VERIFIED','MYSQL_PENDING']:print('ISSUE',id,status['status'],str(status.get('error') or status.get('failures'))[:350],flush=True)
  if n%20==0:print('verified',n,flush=True)
(R/'progress/题库校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('DONE',len(report),flush=True)
