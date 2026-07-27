# QuantaForge 提交包说明

作品方向：赛道四“壁仞飞翔杯·量子计算”，赛题一“量子计算模拟与算法演示平台”。

## 首次查看顺序

1. `SKILL.md`：技能入口、输入输出契约和失败策略。
2. `README.md`：环境、运行、测试和目录说明。
3. `docs/scenario.md`：应用场景与代表性任务。
4. `docs/architecture.md`、`docs/agent_workflow.md`：架构与 Agent 闭环。
5. `reports/generated/correctness_report.md`：四类算法实测摘要。
6. `docs/validation_report.md`、`docs/performance_analysis.md`：验证与性能解释。
7. `presentation/QuantaForge_competition_deck.pptx`：8 页答辩材料。

## 最终验收状态

- 本地确定性单元测试：8 / 8 通过。
- 赛事 GPU 完整正确性套件：4 / 4 通过。
- Bell、GHZ、Grover CPU/GPU 关键结果差：0。
- QAOA 4 节点环图：割值 4，经典精确最优值 4，近似比 1.0。
- 提交结构检查：12 个必需文件齐全，6 段开发交互记录，敏感标记扫描通过。
- PPT：8 页，自动溢出检测通过并完成逐页视觉检查。

## 一键复验

```bash
source /usr/local/birensupa/br_container_tools/brsw_set_env.sh
export PYTHONPATH="$PWD/src"
python3 -m unittest discover -s tests -v
python3 scripts/validate_correctness.py
python3 scripts/benchmark.py --sizes 8,12,16,20,22,24,25,26 --warmups 2 --repeats 7 --batch-size 1
python3 scripts/check_submission.py
```
