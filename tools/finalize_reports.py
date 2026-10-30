import json,pathlib,collections
R=pathlib.Path(__file__).resolve().parents[1];index=json.loads((R/'catalog/index.json').read_text());quality=json.loads((R/'progress/题库校验.json').read_text());mut=json.loads((R/'progress/变异测试总报告.json').read_text());sql=json.loads((R/'progress/SQL测试准备.json').read_text());review=json.loads((R/'progress/变异幸存项人工复核.json').read_text());canonical=json.loads((R/'catalog/canonical.json').read_text())
# Update human-readable per-problem reports, never change the underlying outcomes.
for sid,rel in canonical.items():
 q=R/rel;v=quality[sid];is_sql=v['status']=='MYSQL_PENDING'
 if is_sql:
  c=sql[sid];md=f'# LC{sid} 测试准备情况\n\n- 用例数：{c["cases"]}\n- 已固定预期：{c["fixedExpected"]}\n- 其余用例：首次实库运行时由参考查询产生预期，并显示预期来源。\n- MySQL实库验证：待用户安装并配置MySQL8后执行。\n- 缺少数据库、参考与固定预期不一致都不会判通过。\n'
 else:
  outcomes=mut.get(sid,{}).get('mutations',[]);killed=sum(m['status'].startswith('KILLED')for m in outcomes);md=f'# LC{sid} 测试质量\n\n- 参考实现状态：{v["status"]}\n- 用例数：{v["cases"]}\n- 独立Python预期用例：{v["independentOracleCases"]}\n- 其他预期：参考实现计算，并在后续运行复核。\n- 捕获错误变异：{killed}/{len(outcomes)}（不含无效变异或等价性折算）。\n'
  if sid in review['equivalentByInspection']:md+='- 幸存的边界变异已人工复核为当前约束下等价：'+review['equivalentByInspection'][sid]+'\n'
 md+='\n这些是有限测试证据，不是所有输入的正确性证明。请在每轮结束使用AI复核材料独立检查算法、反例和复杂度。\n';(q/'测试/质量说明.md').write_text(md)
counts=collections.Counter(m['status']for v in mut.values()for m in v['mutations']);algo=[v for v in quality.values()if v['status']=='REFERENCE_VERIFIED'];total=sum(v['cases']for v in algo);independent=sum(v['independentOracleCases']for v in algo)
md=f'''# 测试质量报告

核对日期：2026-10-30。工程含350个题单位置、283道不同题目；算法183道，SQL100道。这里记录工程验证，不代表用户学习完成。

| 项目 | 结果 |
|---|---:|
| Java参考实现编译并通过本地用例 | {len(algo)}/183 |
| 算法用例 | {total} |
| 其中独立Python预期 | {independent} |
| 其中参考实现计算预期 | {total-independent} |
| SQL准备的用例 | {sum(v['cases']for v in sql.values())} |
| SQL已有固定预期 | {sum(v['fixedExpected']for v in sql.values())} |
| SQL独立规则与公开示例交叉核对 | 40题 |
| MySQL实库执行 | 待安装与配置 |
| 引擎断言自测 | 20项通过 |
| 生命周期集成验证 | 新建、暂停、继续、测试、结束、导出、复做、删除、错误答案通过 |
| Maven完整编译 | 通过 |

## 变异检查

生成319个候选变异：{counts['KILLED']}个被用例捕获，{counts['KILLED_TIMEOUT']}个因超时被捕获，1个无法编译不计作检测成功。11个幸存边界变异经逐一查看源码，属于当前题目约束下的等价变化；具体理由见[人工复核](变异幸存项人工复核.json)。这些候选不是完整变异空间，不能把捕获比例当覆盖率或正确率。

曾发现LC14的首字符串比后续字符串短时缺少边界用例，已补充反例并重新验证，该非等价变异已被捕获。也修复了用例生成中的共享可变数组、整数比较错误容差、空链表规范化和约束外输入问题。

## 判题边界

- 原地修改检查有效前缀或原对象变化，多答案按题意校验，不强制与参考选择完全相同。
- 深拷贝检查原对象保持与引用不共享；环入口、链表交点和树节点使用原对象身份。
- SQL按列名对齐、按题意决定是否比较行序，保留NULL与重复行数量。每个样例隔离运行。
- 算法复杂度与随机集合均匀性没有被有限功能测试完整证明；已加入部分规模边界，但仍需独立代码复核。
- 1944个参考预期用例（若后续统计变化，以表格为准）存在与参考实现共享错误的可能；没有把它们计入独立预期。
- SQL没有本机MySQL环境，目前不能声明查询、预期和方言已在MySQL8上全部通过；首次实库运行会先校验参考与固定预期，冲突时阻止通过。

## 可追溯文件

- [逐题参考校验](题库校验.json)
- [逐题变异记录](变异测试总报告.json)
- [SQL用例准备](SQL测试准备.json)
- [SQL独立预期核对](SQL独立预期交叉核对.json)
- 各题目录的测试/cases.json或测试/sql-cases.json以及质量说明.md

进阶SQL题号采用公开索引交叉核对，官方会员题单分类尚待核实；此项不会伪装成官方接口完整导入。
'''
md=md.replace('1944个参考预期用例',str(total-independent)+'个参考预期用例');(R/'progress/测试质量报告.md').write_text(md)
plans=[('top-interview-150','01-面试经典150'),('top-100-liked','02-Hot100'),('sql-free-50','03-SQL/01-SQL基础50'),('sql-premium-50','03-SQL/02-SQL进阶50')]
for plan,parent in plans:
 rows=[x for x in index if x['plan']==plan];text='# '+parent.split('/')[-1]+'\n\n运行题目入口的Start.java开始练习。重复题按题号汇总历史，题单位置分别保留。\n\n'
 if plan=='sql-premium-50':text+='题号来自两份公开索引交叉核对，分类为教学分组，官方分类待核对。\n\n'
 text+='| 题号 | 题目 | 难度 | 分类 | 入口 |\n|---|---|---|---|---|\n'
 for x in rows:
  q=R/x['path'];cfg=json.loads((q/'题目配置.json').read_text());rel=q.relative_to(R/parent);entry='入口/src/main/java/'+x['class'].replace('.','/')+'.java';text+=f'| LC{x["id"]} | [{cfg["titleCn"]}]({rel}/题目.md) | {cfg["difficulty"]} | {cfg["category"]} | [Start]({rel}/{entry}) |\n'
 (R/parent/'README.md').write_text(text)
print('REPORTS',total,independent,dict(counts))
