# test-engineer

测试工程师框架 - 将测试全流程（需求→设计→执行→报告→归档）整合为一个 Claude Code skill。

## 安装

```bash
git clone <仓库地址>
cd test-engineer
./scripts/install.sh
```

安装脚本会引导你：
1. 选择业务配置包（preset）
2. 填写基本配置（姓名、Jira 用户名、输出目录）
3. 创建 skill symlink 到 `~/.claude/skills/test-engineer`

## 使用

在 Claude Code 中直接说：

| 说什么 | 做什么 |
|---|---|
| "开始 A2.26 版本测试" | 初始化版本，创建状态文件 |
| "添加需求：xxx" | 智能路由创建/复用/更新需求 |
| "生成测试用例" | 生成测试用例（平台线）或测试方案（算法线） |
| "测试进度" | 显示进度看板 |
| "写测试报告" | 生成测试报告 |
| "帮我审一下这批用例" | 测试专家评审 |
| "这个场景怎么测" | 测试专家咨询 |

## 创建自己的 preset

复制 `presets/example/` 目录，修改以下文件：

- `preset.yaml` - 产品名、版本号格式、启用的模块
- `test-expert.md` - 你的产品线测试专家角色定义
- `product-knowledge.md` - 产品基本信息
- `knowledge-base/` - 业务规则、缺陷模式、系统基线
- `report-config.md` - 报告格式和模板

## 卸载

```bash
./scripts/uninstall.sh
```

## 架构

```
test-engineer/
├── test-engineer/          # skill（单入口）
│   ├── SKILL.md            # 路由 + 版本管理
│   ├── modules/            # 功能模块（按需加载）
│   ├── shared/             # 数据契约 + 接口定义
│   └── references/         # 脚本和模板
├── presets/                 # 业务配置包
│   ├── example/            # 示例（公开）
│   └── kavabot/            # 实际业务数据（.gitignore）
├── config/                  # 用户配置
└── scripts/                 # 安装/卸载脚本
```
