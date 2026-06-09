# test-engineer

测试工程师 Skill —— 将测试全流程（需求 → 设计 → 执行 → 报告 → 归档）整合为一个 Claude Code Skill。

## 架构

```
test-engineer-skill/（本仓库，公开）
├── test-engineer/           ← 框架代码（SKILL.md + 模块 + 共享定义）
├── config/                  ← config.example.yaml（模板）
├── presets/example/         ← 通用示例 preset
└── scripts/                 ← install.sh / uninstall.sh

test-engineer-private/（私有仓库）
├── config/config.yaml       ← 你的私有配置
├── presets/{产品}/           ← 产品 preset + 产品知识
├── shared-knowledge/
│   ├── knowledge-base/      ← 通用测试方法论/行业标准
│   └── {产品}/              ← 产品专项知识库（代码模块/业务规则/诊断/基线）
└── link.sh                  ← 挂载脚本
```

## 安装

### 1. 克隆仓库

两个仓库放在同一目录下：

```bash
# 公开仓库（框架代码）
git clone https://github.com/18520500303/test-engineer-skill.git

# 私有仓库（产品配置 + 知识库，需要权限）
git clone git@github.com:18520500303/test-engineer-private.git
```

### 2. 运行安装脚本

```bash
cd test-engineer-skill
bash scripts/install.sh
```

安装脚本会自动：
1. 检测 Claude Code 环境（`~/.claude/`）
2. 创建 symlink：`~/.claude/skills/test-engineer → repo/test-engineer/`
3. 检测同目录下的 `test-engineer-private`，自动运行 `link.sh` 挂载：
   - presets → `~/.claude/skills/presets/`
   - config → `~/.claude/skills/config/`
   - shared-knowledge → `~/.claude/skills/shared-knowledge/`
4. 生成 `config.yaml`（选择 preset）

### 3. 验证

在 Claude Code 中输入 `/test-engineer`，应看到版本管理界面。

### 仅使用公开框架（无产品数据）

如果没有私有仓库权限，只 clone 本仓库即可使用通用框架：

```bash
git clone https://github.com/18520500303/test-engineer-skill.git
cd test-engineer-skill
bash scripts/install.sh
# 选择 example preset
```

需要自行创建产品 preset（见下方"创建自己的 preset"）。

## 使用

在 Claude Code 中直接说：

| 说什么 | 做什么 |
|---|---|
| "开始 A2.26 版本测试" | 初始化版本，创建状态文件 |
| "添加需求：xxx" | 智能路由创建/复用/更新需求 |
| "生成测试用例" | 平台线用例（Excel + JSON）或算法线方案 |
| "测试进度" | 显示进度看板 |
| "写测试报告" | 生成测试报告（算法/平台/专项） |
| "版本更新说明" | 客户版更新公告 |
| "归档" | 归档版本测试资产 |
| "帮我审一下这批用例" | 测试专家评审 |
| "这个场景怎么测" | 测试专家咨询 |
| "学习 xxx" | 外部知识学习 |

## 创建自己的 preset

复制 `presets/example/` 目录到你的私有仓库的 `presets/` 下：

```bash
# 在 test-engineer-private 仓库中
cp -r ../test-engineer-skill/presets/example presets/my-product
```

需要修改的文件：

| 文件 | 说明 |
|------|------|
| `preset.yaml` | 产品名、版本号格式、启用模块、路径、Jira 项目映射 |
| `product-knowledge.md` | 产品基本信息（硬件/软件/功能） |
| `test-expert.md` | 产品线测试专家角色定义 |
| `report-config.md` | 报告格式和模板 |

然后在 `shared-knowledge/` 下创建产品知识库：

```
shared-knowledge/my-product/
├── business-rules/       ← 业务规则
├── code-modules/         ← 代码模块知识（overview/interfaces/test-points）
├── defect-patterns/      ← 缺陷模式
├── diagnosis/            ← 问题诊断
├── system-baselines/     ← 系统基线
└── INDEX.md              ← 索引
```

重新运行 `link.sh` 挂载新 preset。

## 卸载

```bash
cd test-engineer-skill
bash scripts/uninstall.sh
```

## License

MIT
