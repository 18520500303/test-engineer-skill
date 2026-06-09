# test-engineer 框架内部约定

## 双仓库架构

- **test-engineer-skill**（本仓库）：框架代码，公开可用
- **test-engineer-private**（私有仓库）：产品 preset + 知识库 + 配置

## 路径约定

SKILL.md 通过变量引用定位所有资源（由 preset.yaml 定义）：

```yaml
paths:
  output_root: "~/Desktop/workdata/测试"
  test_expert: "../sweeper-robot-test/SKILL.md"
  shared_knowledge: "../shared-knowledge/knowledge-base/"
  knowledge_base: "../shared-knowledge/{产品}/"
  product_knowledge: "../shared-knowledge/{产品}/platform-app-product-knowledge.md"
  jira_mapping: "../shared-knowledge/{产品}/jira-projects.md"
```

模块中使用变量引用：
- `{output.root}` — 文件输出根目录
- `{paths.knowledge_base}` — 产品专项知识库
- `{paths.shared_knowledge}` — 通用知识库
- `{jira_projects.platform_defect}` — Jira 项目名

**禁止硬编码**绝对路径或 Jira 项目名。

## 模块编写规范

- 不写 YAML frontmatter（只有 SKILL.md 有）
- 第一行为 `> 数据契约见 shared/definitions.md，模块协作见 shared/interfaces.md。`
- 不引用绝对路径，用 `{paths.*}` 和 `{output.root}` 变量
- 不自行归档，归档由 SKILL.md 统一调 archive-manager
- 不重复调 performance-baseline IF-9（由 req-manager 统一调用）
- JQL 查询用 `{jira_projects.*}` 变量，不硬编码项目名
- 产品特有约束（如平台功能限制）放产品知识层，不放模块中

## 加载策略

- SKILL.md 保持 500 行以内
- 模块按需 Read，不预加载
- 产品知识按话题按需加载
- 版本管理逻辑膨胀时拆到 modules/version-lifecycle.md
