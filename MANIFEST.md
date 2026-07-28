# QuantaForge 提交包说明

作品方向：赛道四“壁仞飞翔杯·量子计算”，赛题一“量子计算模拟与算法演示平台”。

## 首次查看顺序

1. `agent交互记录.md`、`agent交互记录/`：9段真实原始Agent问答、完整JSON和运行日志。
2. `qa/results/qa_report.md`：可复现QA实测结果。
3. `SKILL.md`：技能入口、输入输出契约和结构化失败策略。
4. `README.md`：环境、运行、测试和目录说明。
5. `docs/scenario.md`：应用场景与代表性任务。
6. `docs/architecture.md`、`docs/agent_workflow.md`：架构与 Agent 闭环。
7. `reports/generated/correctness_report.md`：四类算法实测摘要。
8. `docs/validation_report.md`、`docs/performance_analysis.md`：验证与性能解释。
9. `presentation/QuantaForge_competition_deck.pptx`：8 页答辩材料。

## 最终验收状态

- 自动单元/接口测试：19 / 19 通过。
- 可复现QA：9 / 9通过，其中4条正常算法实跑、5条异常结构化拒绝。
- 原始Agent交互：9段，每段含请求、完整响应、运行日志和自动核验。
- 赛事 GPU 完整正确性套件：4 / 4 通过。
- Bell、GHZ、Grover CPU/GPU 关键结果差：0。
- QAOA 4 节点环图：割值 4，经典精确最优值 4，近似比 1.0。
- 提交结构检查：必需文件齐全，8段开发摘要和9段原始Agent交互均可定位，敏感标记扫描通过。
- PPT：8 页，自动溢出检测通过并完成逐页视觉检查。

## 一键复验

```bash
source /usr/local/birensupa/br_container_tools/brsw_set_env.sh
export PYTHONPATH="$PWD/src"
python3 -m unittest discover -s tests -v
python3 qa/run_reproducible_qa.py
python3 scripts/validate_correctness.py
python3 scripts/benchmark.py --sizes 8,12,16,20,22,24,25,26 --warmups 2 --repeats 7 --batch-size 1
python3 scripts/check_submission.py
```
