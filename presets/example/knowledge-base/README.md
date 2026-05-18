# 知识库

在这里放置你的业务规则、缺陷模式和系统基线文件。

## 目录结构

```
knowledge-base/
├── business-rules/     # 业务规则（按功能域组织）
├── defect-patterns/    # 高频缺陷模式
└── system-baselines/   # 系统行为基线（设备规格、服务列表等）
```

每个子目录可包含任意 `.md` 或 `.json` 文件，test-expert 会按话题按需加载。
