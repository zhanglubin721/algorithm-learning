import pathlib,json,sys,collections
from sql_fixtures import oracle,parse_output
R=pathlib.Path(__file__).resolve().parents[1];C=pathlib.Path('/private/tmp/algorithm-source-cache');idx=json.loads((R/'catalog/canonical.json').read_text());notes=[];checked=0
for sid,rel in idx.items():
 q=R/rel;cfg=json.loads((q/'题目配置.json').read_text())
 if cfg['kind']!='sql':continue
 d=json.loads((C/sid/'detail.json').read_text());sample=d.get('sampleTestCase');examples=parse_output((C/sid/'README.md').read_text())
 if not sample or not examples:notes.append({'id':sid,'status':'NO_PUBLISHED_EXPECTATION'});continue
 expected=oracle(int(sid),json.loads(sample))
 if expected is None:continue
 actual=examples[0];headers=[x.lower()for x in expected[0]];headers2=[x.lower()for x in actual[0]]
 if set(headers)!=set(headers2):notes.append({'id':sid,'status':'HEADER_DISAGREEMENT','python':expected,'published':actual});continue
 ar=[[row[headers2.index(col)]for col in headers]for row in actual[1]]
 if sorted(map(str,expected[1]))!=sorted(map(str,ar)):notes.append({'id':sid,'status':'VALUE_DISAGREEMENT','python':expected,'published':actual})
 else:checked+=1
out={'independentOraclesCheckedAgainstPublishedExamples':checked,'notes':notes,'mysqlExecuted':False};(R/'progress/SQL独立预期交叉核对.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
