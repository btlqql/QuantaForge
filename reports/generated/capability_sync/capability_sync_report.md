# GHZ 26比特能力边界同步实测

- 平台：Biren106M，32,512 MiB显存
- Git提交：`6ca7dd95eaaa6c98b4baf55fd05c6cc36e745b75`
- 测试路径：Web API → Agent → UnitaryLab → Biren GPU → 完整状态验证 → 有界JSON响应
- 测试日期：2026-07-28

## 26比特合法请求

- 请求：`用26个量子比特构建GHZ态，使用壁仞GPU运行并验证`
- 状态：`success`
- GPU执行时间：`7.939913842s`
- 完整状态维度：`67,108,864`
- 解析最大误差：`2.980232239e-08`
- 概率和误差：`5.960464478e-08`
- 正确性验证：`PASS`
- Web概率输出：`sparse_nonzero`，只返回`|00…0⟩`和`|11…1⟩`两个非零态

完整状态向量参与数值验证；仅展示响应被压缩，因此能力扩展不会产生数千万条JSON标签。原始结果见`ghz26_web_result.json`，线路见`ghz26_quantum_circuit.svg`。

## 27比特越界请求

- HTTP状态：`422`
- 错误代码：`CAPABILITY_LIMIT_EXCEEDED`
- 请求值：`27`
- 允许范围：`3`至`26`
- `verification.executed=false`

原始结构化响应见`ghz27_structured_error.json`。
