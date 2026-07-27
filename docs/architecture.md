# 系统架构与调用链

## 设计目标

QuantaForge解决量子实验使用门槛高、参数容易配置错误、运行结果难以独立核验、GPU过程缺少证据的问题。

## 调用链

```text
Web / CLI
  → QuantumExperimentAgent
    → NaturalLanguageParser
      → ExperimentSpec.validate
        → ExperimentPlanner
          → UnitaryLabExecutor
            → Biren GPU / CPU
          → IndependentVerifier
            → Analytic / Exhaustive / Cross-device
        → ExperimentResult
      → JSON + SVG + LOG + Markdown
```

## 关键设计

### 结构化协议

自然语言不会直接转换为任意代码，而是转换为白名单结构 `ExperimentSpec`。所有整数范围、目标串、图边和设备都经过确定性检查。

### 执行与验证分离

执行层使用UnitaryLab，验证层不复用算法内部的“成功”字段：Bell/GHZ使用解析向量；Grover重新计算理论迭代与概率；QAOA穷举经典最优解。

### 证据优先

每次运行分配唯一任务ID，产物保存在独立目录。结果JSON包含输入、任务链、设备指标、验证方法、误差和产物URL。

