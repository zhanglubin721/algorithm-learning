"""Real compilation/execution tests for the new quick-example workflow."""
from project_env import ROOT, JAVA_BIN
import json, pathlib, shutil, subprocess, tempfile

root = ROOT
index = json.loads((root / 'catalog/canonical.json').read_text())
base = pathlib.Path(tempfile.mkdtemp(prefix='example-smoke-', dir=root / '.cache'))
checks = []

def invoke(class_name, relative, data=''):
    p = subprocess.run([JAVA_BIN + 'java', '-cp', str(root / '.cache/engine'), class_name, relative],
                       cwd=root, input=data, text=True, capture_output=True, timeout=60)
    return p

for sid in ['1', '88', '146']:
    q = base / sid
    q.mkdir()
    original = root / index[sid]
    for name in ['题目配置.json', '题目.md']:
        shutil.copy2(original / name, q / name)
    for name in ['模板', '测试', '题解']:
        shutil.copytree(original / name, q / name)
    rel = str(q.relative_to(root))
    p = invoke('engine.Main', rel, '1\n0\n')
    assert p.returncode == 0, p.stderr
    a = q / json.loads((q / '作答/current.json').read_text())['path']
    assert (a / '本地用例.json').exists()
    session = json.loads((a / 'session.json').read_text())
    pkg = session['package']
    code = 'package ' + pkg + ';\nimport java.util.*;\n' + (q / '题解/Solution.java.reference').read_text()
    (a / 'Solution.java').write_text(code)
    session_before = (a / 'session.json').read_bytes()
    p = invoke('engine.ExampleTest', rel)
    assert p.returncode == 0, p.stderr
    sample = json.loads((a / '示例测试结果.json').read_text())
    assert sample['status'] == 'EXAMPLE_PASS' and sample['passed'], p.stdout
    assert '输入：' in p.stdout and '预期：' in p.stdout and '实际：' in p.stdout
    assert not (a / '测试结果.json').exists(), '示例结果污染完整判题'
    assert (a / 'session.json').read_bytes() == session_before, '示例测试改变了计时状态'
    p = invoke('engine.Main', rel, '2\n5\n1\n0\n')
    assert not json.loads((a / 'session.json').read_text())['localPassed'], '示例通过不应计为完整通过'
    assert ' 分 ' in p.stdout and ' 秒' in p.stdout and '本地通过=' not in p.stdout
    checks.append(f'LC{sid}: examples/display/timer/full-pass-isolation')
    if sid == '1':
        local = [{'name':'自定义','args':[[3,3],6],'expected':[0,1]}]
        (a / '本地用例.json').write_text(json.dumps(local))
        p = invoke('engine.ExampleTest', rel)
        assert json.loads((a / '示例测试结果.json').read_text())['passed'], p.stdout
        assert json.loads((a / '本地用例.json').read_text()) == local, '用户用例被覆盖'
        (a / 'Solution.java').write_text('package '+pkg+'; class Solution { public int[] twoSum(int[] a,int b){return new int[]{0,0};}}')
        p = invoke('engine.ExampleTest', rel)
        assert not json.loads((a / '示例测试结果.json').read_text())['passed'], '错误答案被接受'
        (a / 'Solution.java').write_text('package '+pkg+'; class Solution { syntax error }')
        p = invoke('engine.ExampleTest', rel)
        assert json.loads((a / '示例测试结果.json').read_text())['status'] == 'COMPILE_ERROR'
        # Compatibility: pre-existing attempts get their example file on first quick test.
        (a / 'Solution.java').write_text(code)
        (a / '本地用例.json').unlink()
        p = invoke('engine.ExampleTest', rel)
        assert (a / '本地用例.json').exists() and json.loads((a / '示例测试结果.json').read_text())['passed']
        (a / '本地用例.json').write_text('[]')
        p = invoke('engine.ExampleTest', rel)
        assert p.returncode != 0 and '不能为空' in p.stderr
        checks.extend(['custom cases preserved', 'wrong answer rejected', 'compile error rejected', 'old attempts supported', 'empty sample rejected'])

(root / 'progress/示例测试入口验证.json').write_text(json.dumps({'status':'PASS','checks':checks,'mysqlExecuted':False,'ideaUiClicked':False},ensure_ascii=False,indent=2))
print('EXAMPLE SMOKE PASS:', ', '.join(checks))
