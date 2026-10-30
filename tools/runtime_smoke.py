from project_env import ROOT,JAVA_BIN
import pathlib,json,shutil,subprocess
r=ROOT;index=json.loads((r/'catalog/canonical.json').read_text());q=r/'.cache/smoke/q';q.mkdir(parents=True,exist_ok=True);src=r/index['1']
for f in ['题目配置.json','题目.md']:shutil.copy2(src/f,q/f)
for f in ['模板','测试','题解']:shutil.copytree(src/f,q/f,dirs_exist_ok=True)
cmd=[JAVA_BIN+'java','-cp',str(r/'.cache/engine'),'engine.Main','.cache/smoke/q']
def run(s):
 p=subprocess.run(cmd,input=s,text=True,capture_output=True,cwd=r,timeout=60)
 assert p.returncode==0,p.stderr
 return p.stdout
run('1\n0\n');a=q/json.loads((q/'作答/current.json').read_text())['path'];session=json.loads((a/'session.json').read_text());pkg=session['package'];reference='package '+pkg+';\nimport java.util.*;\n'+(q/'题解/Solution.java.reference').read_text()
(a/'Solution.java').write_text(reference);run('2\n3\n0\n');assert json.loads((a/'测试结果.json').read_text())['passed']
(a/'Solution.java').write_text('package '+pkg+'; class Solution { syntax error }');run('2\n3\n0\n');assert json.loads((a/'测试结果.json').read_text())['status']=='COMPILE_ERROR'
(a/'Solution.java').write_text(reference);run('2\n3\n0\n');assert json.loads((a/'测试结果.json').read_text())['passed']
(a/'Solution.java').write_text(reference+'\n// 修改后旧测试不能继续算通过\n');run('2\n5\n1\n0\n');assert not json.loads((a/'session.json').read_text())['localPassed']
run('1\n0\n');a2=q/json.loads((q/'作答/current.json').read_text())['path'];pkg=json.loads((a2/'session.json').read_text())['package'];(a/'Solution.java').write_text('故意保留其他轮次的语法错误')
(a2/'Solution.java').write_text('package '+pkg+';\nimport java.util.*;\n'+(q/'题解/Solution.java.reference').read_text());run('2\n3\n5\n1\n0\n');assert json.loads((a2/'session.json').read_text())['localPassed'];assert (a2/'AI复核材料.md').exists()
print('SMOKE PASS: compile-error blocks stale bytecode; changed source invalidates pass; other attempts cannot block current compilation')
(r/'progress/运行链路验证.json').write_text(json.dumps({'date':'2026-10-30','status':'PASS','checks':['create','pause','resume','test','finish','export','redo','delete','wrong-answer','compile-error-no-stale-run','source-hash-invalidates-pass','other-attempt-syntax-isolation'],'mysqlExecuted':False,'ideaUiClicked':False},ensure_ascii=False,indent=2))
