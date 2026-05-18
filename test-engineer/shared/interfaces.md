# 模块协作关系

## 整体流程

```
用户输入
    ↓
SKILL.md（路由 + 版本管理）
    ↓
┌─────────────────────────────────────────────────┐
│ 阶段1：需求处理                                   │
│   req-manager → 需求文档                          │
│     ↓ 调用 performance-baseline IF-9 规划基线      │
│     ↓ 路由到算法线或平台线                         │
├─────────────────────────────────────────────────┤
│ 阶段2：测试设计                                   │
│   算法线 → test-expert（测试方案+测试点）           │
│   平台线 → test-case-generator（测试用例+Excel）   │
│     ↓ 自动验证（API校验+覆盖度+冗余）             │
│     ↓ 交叉复核（test-expert + test-case-generator）│
├─────────────────────────────────────────────────┤
│ 阶段3：执行测试                                   │
│   test-data-manager（记录测试结果）               │
├─────────────────────────────────────────────────┤
│ 阶段4：生成报告                                   │
│   算法线 → algo-test-report                       │
│   平台线 → platform-test-report                   │
│   更新说明 → release-notes                        │
├─────────────────────────────────────────────────┤
│ 阶段5：归档                                       │
│   archive-manager                                │
└─────────────────────────────────────────────────┘
```

## 标准接口定义

| 接口 | 方向 | 用途 |
|---|---|---|
| IF-003 | req-manager → test-expert / test-case-generator | 测试点设计输出 |
| IF-004a | SKILL.md → algo-test-report | 算法测试报告生成 |
| IF-004b | SKILL.md → platform-test-report | 平台测试报告生成 |
| IF-009 | req-manager → performance-baseline | 基线指标规划（早期介入） |

## 辅助模块（按需调用，不绑定阶段）

| 模块 | 调用时机 |
|---|---|
| archive-manager | 归档阶段 + 复用查询（任意阶段） |
| test-data-manager | 执行阶段记录结果 + 报告阶段读取数据 |
| performance-baseline | 需求阶段规划指标 + 报告阶段对比基线 |
| release-notes | 报告阶段生成客户版更新说明 |

## 专家模式（独立于流程）

```
用户咨询 → SKILL.md 识别为专家模式 → 加载 test-expert + knowledge-base
（无状态，不写入版本状态文件）
```
