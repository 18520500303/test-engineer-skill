# Evolution Log

## 2026-05-29

- [prompt] SKILL.md 核心约束新增：资源约束≠删测试范围，遇条件受限先找替代方法
  - 触发信号：1条 high severity user_correction（欢创F2C1专项，删除精度测试）
  - 审批状态：已批准
- [prompt] SKILL.md 自评审新增第5条：沉淀即时执行，禁止只口头总结不写文件
  - 触发信号：1条 medium severity user_correction（复盘未沉淀）
  - 审批状态：已批准

## 2026-05-18 (v2 — 框架改造)

- [框架] 消除 preset 启动依赖：config.yaml/preset.yaml 改为可选，内置 C3 默认配置
- [框架] 退役 test-flow-manager 及 8 个重复独立 skill（algo-test-report, platform-test-report, req-manager, test-case-generator, test-data-manager, performance-baseline, archive-manager, release-notes-generator）
- [框架] 所有 preset 间接路径改为直接路径（../shared-knowledge/, ../sweeper-robot-test/）
- [框架] evolution.md 重写：新增信号收集 + Prompt 层自进化 + 人工审批流
- [框架] SKILL.md 自评审新增信号采集步骤（user_correction / bottleneck）+ 进化提醒
- [框架] 新建 evolution-signals.jsonl 信号存储文件
- [框架] 8 个模块添加 `<!-- evolution:mutable -->` 标记，定义可进化边界

## 2026-05-18

- [框架] test-engineer 框架初始版本完成，整合 10 个独立测试 skill 为单入口架构
- [框架] 新增自评审机制（质量检查 + 沉淀检查），每个阶段完成后自动执行
- [框架] 新增错误恢复建议，5 个错误场景均补充具体恢复策略
- [框架] 新增自进化模块（evolution.md），支持知识沉淀、知识库回顾、流程效率分析
