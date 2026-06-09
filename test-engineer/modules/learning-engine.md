> 数据契约见 shared/definitions.md，模块协作见 shared/interfaces.md。

# 学习引擎模块

管理外部知识获取、处理、审核和源/策略进化。支持被动按需学习和主动定时学习。

---

## 触发场景

| 触发词 | 场景 | 动作 |
|---|---|---|
| "学习 {主题}" / "搜索 {XX}" / "上网查 {XX}" | 按需快速学习 | 执行快速模式 |
| "深入研究 {主题}" / "系统分析 {XX}" | 按需深度学习 | 执行深度模式 |
| "查查竞品 {XX}" | 竞品学习 | 自动判断快速/深度 |
| "开启自动学习" | 启动定时任务 | 创建 CronCreate |
| "关闭自动学习" | 关闭定时任务 | 执行 CronDelete |
| "学习源列表" | 查看源 | 展示源表 |
| "添加学习源 {URL/名称}" | 注册新源 | 写入 learning-sources.yaml |
| "移除学习源 {名称}" | 归档源 | 更新 status→archived |
| "搜索策略状态" | 查看策略 | 展示策略表 + 效率 |
| "优化搜索策略" | 手动触发优化 | 执行策略进化 |
| "审核学习成果" | 批量审核 | 展示待审列表 |
| "代码学习" / "学习代码" / "继续代码学习" | GitLab 代码学习 | 执行当日计划，产出写入 code-modules |
| "代码学习进度" | 查看计划进度 | 展示 gitlab-learning-plan 状态 |

---

## 一、快速模式

### 执行步骤

1. **加载配置**：读取 `learning-sources.yaml` + `learning-strategies.yaml`
2. **选择策略**：根据用户主题匹配最相关的 strategy（按 category 关键词匹配）
3. **执行搜索**：
   - 用 `keywords_template` 替换 `{topic}` 和 `{year}` 后调用 WebSearch
   - 搜索 2-3 次（search_depth 决定）
4. **选取结果**：WebFetch 抓取 top 3，优先级：
   - URL 属于已注册信息源（status=active）→ 最优先
   - 域名为知名技术站点（.edu、知名技术博客、官方文档）→ 次优
   - 其余按搜索排名
5. **提取与分类**：
   - 提取核心要点、应用场景、原始摘要
   - 判断 category（methodologies / competitive / industry-standards / technical-references）
   - 分配 tags
6. **去重检查**（详见第四章）
7. **判断价值**：
   - 高价值标准：与当前活跃版本相关 / 填补知识库空白 / 来自高优先级源 / 行业标准变更
   - 不满足以上 → 低价值
8. **写入待审区**：
   - 高价值 → `external-learning/pending/high/{date}-{kebab-title}.md`
   - 低价值 → `external-learning/pending/low/{date}-{kebab-title}.md`
9. **通知**：
   - 高价值 → 立即展示摘要 + 尝试微信推送（wechat-claude-code）
   - 推送失败 → 写入 `external-learning/pending-notifications.md`
   - 低价值 → 仅记录，等待汇总
10. **更新策略统计**：execution_count + 1，更新 effectiveness

### 知识条目写入格式

```markdown
---
title: "{提取的标题}"
source_url: "{原始URL}"
source_name: "{源名称}"
fetched_date: {YYYY-MM-DD}
category: {category}
priority: {high|low}
tags: [{相关标签}]
strategy_used: {strategy_id}
---

## 核心要点

- {要点1}
- {要点2}
- ...

## 应用场景

- 适用于：...
- 不适用于：...

## 原始摘要

> {简短引用，标注来源}
```

---

## 二、深度模式

### 执行步骤

1. **资源检查**：读取 `learning-progress.yaml` 中 `daily_deep_research_count`
   - 同一天 count ≥ `max_deep_research_per_day`（默认3）→ 提示"今日深度研究额度已用完，明天再试或改用快速模式"并退出
2. **执行前确认**（被动触发时）："深度研究预计需要较多时间和 token，确认继续？"
   - 自动学习中跳过确认
3. **调用 deep-research skill**：传入用户主题
4. **拆解报告**：将综合报告拆解为独立知识条目（每个核心发现一条）
5. **去重 + 分类 + 写入**：同快速模式步骤 6-9
6. **更新计数**：daily_deep_research_count.count + 1，date 设为今天
7. **立即展示**：展示所有产出条目摘要供用户审核

---

## 三、主动定时学习

### 开启自动学习

用户说"开启自动学习"时：

1. 调用 `CronCreate`：
   - cron: 配置的 `auto_schedule`（默认 `"0 22 * * *"`）
   - durable: true
   - recurring: true
   - prompt: "执行测试工程师学习引擎自动学习流程"
2. 记录返回的 job ID 到 `learning-progress.yaml` 的 `cron_job_id`
3. 设置 `cron_created_date` 为今天
4. 确认："自动学习已开启，每天 22:00 执行。注意：需保持 Claude Code 会话在线。7 天后自动续期。"

### 关闭自动学习

用户说"关闭自动学习"时：

1. 读取 `learning-progress.yaml` 中 `cron_job_id`
2. 调用 `CronDelete(id: cron_job_id)`
3. 清空 `cron_job_id` 和 `cron_created_date`
4. 确认："自动学习已关闭。"

### 自动执行流程（CronCreate 触发时）

```
开始
  ↓
1. 续期检查：距 cron_created_date 已过 ≥6 天？
   - 是 → CronDelete(cron_job_id) + CronCreate 重建
   - 更新 cron_job_id / cron_created_date
   ↓
2. 前置清理：
   - 扫描 rejected/ 中 fetched_date 超过 rejected_retention_days 的文件 → 删除
   - 检查 sources-log 文件，超过 sources_log_retention_months 的移入 sources-log-archive/
   ↓
3. 读取 learning-progress.yaml：
   - 有 pending_sources → 优先扫描这些（断点续传）
   - 无 → 按优先级从 learning-sources.yaml 选取（max_sources_per_session 个）
   - dormant 源以 1/3 频率参与（每3天扫描一次）
   ↓
4. 对每个源执行：
   a. 选择匹配的 strategy（按源的 category 匹配）
   b. 执行搜索（受 max_searches_per_session 总控）
   c. WebFetch 抓取（受 max_fetches_per_session 总控）
   d. 提取 + 去重 + 分类 + 写入
   e. 更新源的 last_scanned、last_hit、hit_count
   f. 更新策略的 execution_count、effectiveness
   g. 检查资源限制和时间限制（max_duration_minutes）
      - 超限 → 保存进度到 learning-progress.yaml → 跳出循环
   ↓
5. 自动发现：分析搜索结果中的新域名
   - 高质量（专业、更新频、测试相关）→ 加入 learning-sources.yaml，status=candidate
   ↓
6. 策略进化（每周一次，判断 today 是否为本周首次执行）：
   - 统计各策略 effectiveness
   - effectiveness < 0.2 且 execution_count ≥ strategy_trial_period → 标记待优化
   - 自动生成变体关键词建议（写入日志供下次用户查看）
   ↓
7. 源生命周期维护：
   - 扫描所有 active 源：last_hit 距今 > retire_after_days → status 改为 dormant
   - candidate 源 hit_count > 0 → status 改为 active
   ↓
8. 生成汇总报告 + 明日学习计划
   ↓
9. 通知：
   - 尝试微信推送汇总报告
   - 推送失败 → 写入 pending-notifications.md
   ↓
10. 写入 sources-log：记录本次执行概况
   ↓
11. 保存最终状态到 learning-progress.yaml
```

### 汇总报告格式

```
📋 今日学习汇总（{date}）

【已获取】
- 高价值 {N} 条（待审核）
- 低价值 {N} 条

【策略效率】
- {strategy_id}: {effectiveness}
- ...

【明日学习计划】
- 计划扫描源：{下次优先的源列表}
- 重点方向：{基于版本需求关键词 + 高效策略方向}
- 新增候选源：{今天发现的新源，如有}

{如有续期} 已自动续期 ✓

回复"审核学习成果"进入详细审核。
```

### 学习计划生成逻辑

1. **当前活跃版本关联**（优先）— 尝试读取当前版本 `流程状态.md` 的需求列表，提取技术关键词作为明日搜索的 topic；无活跃版本时跳过
2. **高效策略深挖** — 近期 effectiveness > 0.5 的策略方向继续
3. **轮换覆盖** — 按 last_scanned 排序取最旧的源
4. **候选验证** — status=candidate 的源优先验证

---

## 四、去重逻辑

**检查范围**：`pending/high/` + `pending/low/` + 正式目录中对应 category 的所有 .md 文件。

### 执行步骤

1. **URL 精确匹配**：遍历检查范围内所有 .md 文件的 frontmatter `source_url`
   - 完全相同 → 检查内容是否有增量
     - 无增量 → 跳过（完全重复）
     - 有增量 → 更新已有条目，标注更新日期
2. **语义近似检查**：无 URL 匹配时，检查是否存在 `source_name` 相同或 `tags` 重叠 ≥ 2 个的文件
   - 存在 → AI 判断核心观点是否相同
     - 相同 → 合并（追加来源到已有条目的原始摘要段）
     - 不同 → 保留为独立条目
3. **通过去重** → 正常写入

---

## 五、源管理

### 查看源列表

用户说"学习源列表"时：

读取 `learning-sources.yaml`，按 status 分组展示：

```
📚 学习信息源

【正式源（active）】
| ID | 名称 | 类别 | 优先级 | 上次命中 | 命中次数 |
|---|---|---|---|---|---|
| google-testing-blog | Google Testing Blog | methodologies | high | - | 0 |
| ... |

【候选源（candidate）】
| ... |

【休眠源（dormant）】
| ... |

共 {N} 个源，其中正式 {N}，候选 {N}，休眠 {N}。
```

### 添加学习源

用户说"添加学习源 {URL或名称}"时：

1. 如果提供了 URL → 提取域名，生成 id（kebab-case）
2. 询问 category 和 priority（或从 URL 内容自动推断）
3. 写入 `learning-sources.yaml`，status=candidate
4. 确认："已添加为候选源 '{name}'，下次学习时验证其价值。"

### 移除学习源

用户说"移除学习源 {名称}"时：

1. 匹配 id 或 name
2. 设置 status=archived
3. 确认："已归档 '{name}'，不再扫描。"

---

## 六、策略管理

### 查看策略状态

用户说"搜索策略状态"时：

读取 `learning-strategies.yaml`，展示：

```
🔍 搜索策略状态

| 策略 | 效率 | 执行次数 | 状态 | 上次执行 |
|---|---|---|---|---|
| methodology-search | 0.45 | 12 | 正常 | 2026-05-17 |
| competitive-search | 0.15 | 8 | ⚠️ 待优化 | 2026-05-16 |
| ... |

⚠️ 标记说明：effectiveness < 0.2 且已过试用期（执行 ≥5 次）
试用期中：execution_count < 5 的策略不参与效率评判
```

### 手动优化策略

用户说"优化搜索策略"时：

1. 找出 effectiveness < 0.2 且 execution_count ≥ strategy_trial_period 的策略
2. 对每个待优化策略：
   - 分析历史搜索中哪些关键词命中率高（从 sources-log 中回溯）
   - 生成 2-3 个变体关键词建议
   - 展示建议，用户确认后更新 keywords_template
3. 如果所有策略效率正常 → 提示"所有策略运行良好，无需优化。"

### 添加搜索关键词

用户说"添加搜索关键词 {策略} {关键词}"时：

1. 匹配策略 id
2. 追加关键词到 keywords_template
3. 确认："已添加到策略 '{strategy_id}' 的关键词模板。"

---

## 七、审核流程

### 批量审核

用户说"审核学习成果"时：

1. 扫描 `pending/high/` 和 `pending/low/` 中的 .md 文件
2. 按优先级排序（high 优先）展示列表：

```
📋 待审核知识（共 {N} 条）

【高价值】
1. {title} — {category} — {source_name} — {fetched_date}
2. ...

【低价值】
3. ...

操作：
- "入库 1,2,3" — 选择性通过
- "全部入库" — 批量通过所有
- "丢弃 4,5" — 拒绝指定条目
- "详情 1" — 查看第1条完整内容
```

### 单条审核操作

- **入库**：
  1. 移动文件到正式目录 `knowledge-base/{category}/{fetched_date}-{kebab-title}.md`
  2. 更新对应源的 `last_hit` 和 `hit_count`
  3. candidate 源首次命中 → status 改为 active
- **丢弃**：
  1. 移动到 `rejected/`
  2. 记录 `user_correction` 进化信号到 `evolution-signals.jsonl`
- **修改后入库**：用户编辑内容 → 保存 → 按"入库"流程执行

### 入库文件命名规范

`{category}/{fetched_date}-{kebab-title}.md`

例：`methodologies/2026-05-18-ai-regression-test-prioritization.md`

模块引用方式：test-case-generator、test-expert 等模块按目录读取 `knowledge-base/{category}/` 时，自动包含所有 .md 文件，新入库知识下次模块加载时即可生效。

---

## 八、兜底提醒

每次 SKILL.md 被触发时（路由前），执行兜底检查：

1. 检查 `pending-notifications.md` 是否有"未送达"状态的行 → 有则展示并标记为"已补发"
2. 检查 `pending/high/` 是否有未审核文件 → 有则提示"{N} 条高价值知识待审核，输入'审核学习成果'查看"
3. 检查 `learning-progress.yaml`：
   - `cron_job_id` 不为空（auto_enabled）但 `last_session.date` 不是昨天或今天 → 提示"自动学习可能未执行，是否立即补学？"

---

## 九、与 evolution 模块联动

### 信号产生时机

- 用户在审核时"丢弃"知识条目 → 记录 `user_correction` 信号：
  ```json
  {"date": "{today}", "type": "user_correction", "module": "learning-engine", "context": "用户拒绝了来自 {source_name} 的知识：{title}。strategy: {strategy_used}", "version": "", "severity": "low"}
  ```
- 某策略连续 3 次执行无有效产出 → 记录 `bottleneck` 信号：
  ```json
  {"date": "{today}", "type": "bottleneck", "module": "learning-engine", "context": "策略 {strategy_id} 连续3次无有效产出，effectiveness={value}", "version": "", "severity": "medium"}
  ```

### 进化触发

同一模块累积 ≥3 条未处理信号时，提示用户："学习引擎已累积 {N} 条改进信号，是否触发进化分析？"

---

## 十、GitLab 代码学习

系统学习 cvterobot2.0 代码仓库各模块，沉淀到共享知识库供 kavabot-engineer 和 test-engineer 共同使用。

### 触发场景

| 触发词 | 动作 |
|---|---|
| "代码学习" / "继续代码学习" / "学习代码" | 读取 gitlab-learning-plan.yaml，执行当日计划 |
| "代码学习进度" | 展示整体进度 |
| "跳过今天" / "补学 Day N" | 调整计划 |

### 执行步骤

1. **读取计划**：`gitlab-learning-plan.yaml`，找到当前 `current_day` 对应的条目
   - 如果 status=completed → 自动找下一个 pending
   - 全部 completed → 提示"代码学习计划已全部完成"
2. **克隆/拉取代码**：通过 GitLab API 或 git clone 获取对应项目代码
3. **按 focus 方向学习**：重点阅读架构、接口、状态机、配置等
4. **双重产出**：
   - **原始笔记** → 写入 `{output_dir}/{module-name}.md`（完整学习笔记，保留所有细节）
   - **共享知识** → 写入 `{paths.knowledge_base}code-modules/{module-name}/`：
     - `overview.md`：模块职责、仓库路径、依赖关系、数据流、可观测性（按 `_templates/overview.template.md` 格式）
     - `interfaces.md`：关键函数、配置项、通信协议、日志关键字（按 `_templates/interfaces.template.md` 格式）
     - `test-points.md`：入参边界、状态流转、集成测试点、风险点、变更影响范围（按 `_templates/test-points.template.md` 格式）
5. **更新索引**：更新 `code-modules/index.json`，添加或更新模块条目
6. **推进进度**：current_day 推进到下一个 pending day
7. **展示摘要**：展示学习成果概要 + 下一天计划预告
8. **自动更新计划**（每次学习后必执行）：
   - 将当日条目 status 改为 completed，记录 completed_by 和 completed_date
   - 更新 `stats` 区域（total_modules_in_kb / complete_modules / incomplete_modules）
   - 更新 `last_plan_update` 为今天
9. **自动调整判断**（每次学习后自动执行，对应 plan 中 auto_adjust.rules）：

   **a. 发现新仓库（discover_new_repos）**：
   - 扫描今日学习的代码中 import/依赖的仓库路径
   - 如果引用的仓库不在 `gitlab-learning-plan.yaml` 任何 day 的 projects 中
   - → 自动追加新 day（status: pending），在 note 中标注"由 Day N 学习时发现"
   - → 在 auto_adjust.history 中记录调整

   **b. 补完缺口（fill_gaps）**：
   - 扫描 code-modules/ 所有模块目录，检查三文件完整性
   - 如果有模块缺 test-points.md 或 interfaces.md 且不在任何 pending day 的 focus 中
   - → 检查是否已有"知识补完" day，有则更新其 focus 列表，无则新建
   - → 在 auto_adjust.history 中记录调整

   **c. 依赖检查（dependency_check）**：
   - 今日学习的模块如果在 overview.md 的依赖关系中提到了其他模块
   - 且被依赖模块不在 code-modules/ 中也不在计划中
   - → 追加到最近的 pending day 或新建 day

   **d. 最终总结（final_summary）**：
   - 当所有代码模块 day 都 completed 且无"知识补完" pending day 时
   - → 确认"系统架构总结" day 存在且为最后一个
   - → 如果不存在，自动创建

   **调整输出**：如果有调整，在摘要后追加：
   ```
   📋 计划自动调整：
   - 新增 Day N: {topic}（原因：{reason}）
   - 补完缺口: {modules}（原因：缺少 test-points.md）
   - 无调整 / 共 N 处调整
   ```

### 写入规范

- 写入 code-modules 前必须先读取对应 `_templates/` 模板
- 如果目标模块目录已存在（比如 kavabot-engineer 已经学过），则**合并更新**而非覆盖：
  - overview.md / interfaces.md：补充缺失内容，保留已有内容
  - test-points.md：追加新发现的测试点，不删除已有内容
- updated_by 字段写 "test-engineer"（如果是合并更新，写 "test-engineer + kavabot-engineer"）
- last_updated 写当天日期

### 多项目单日处理

当一天计划包含多个项目时（如 Day 2 有 map_manager + health_center）：
- 每个项目独立创建 code-modules 子目录
- 每个项目独立写入 index.json
- 原始笔记可按项目分文件或合并为单日笔记

---

## 十一、版本触发知识库刷新

每次开始新版本测试时（算法线/平台线/专项均适用），自动扫描 GitLab 上的模块变化：检测现有模块的代码变更、发现新增模块、标记废弃模块，保持知识库与实际代码仓库同步。

### 触发时机

在 SKILL.md "模式一：版本管理" 的 "开始 {版本号} 版本测试" 流程中，**步骤 0**（在创建流程状态文件之前）执行。

### 执行步骤

1. **读取 index.json**：获取所有 65 个模块的 `name`、`repo`、`last_updated`
2. **扫描 Git 变更**：对每个模块，通过 GitLab API 获取该仓库在 `last_updated` 之后的提交记录
   - API: `GET /api/v4/projects/{id}/repository/commits?since={last_updated}&per_page=5`
   - 如果项目 ID 未知，通过 repo 路径搜索：`GET /api/v4/projects?search={repo_name}`
   - 只需检查是否有新提交（不需要读每个 commit 的内容）
3. **检测新增模块**：
   - 扫描 GitLab 组的所有子项目（cvterobot2.0 和 robot-software/cloud-app 两个组）
   - API: `GET /api/v4/groups/{group_id}/projects?per_page=100`（需分页）
   - 对比 index.json，找出不在知识库中的新项目
   - 排除空壳项目（< 5 个文件）和 archive 项目
4. **检测废弃模块**：
   - 检查 index.json 中每个模块的 GitLab 项目是否存在
   - 检查项目是否被标记为 `archived: true`
   - 检查项目最后提交时间是否超过 1 年（可能是废弃项目）
5. **输出变更清单**：
   ```
   📋 知识库变更检测（上次更新: {日期范围}）

   🆕 新增模块（X个）：
   - ✨ new-module-name: 新发现的项目，建议学习入库
   - ...

   ⚠️ 有代码变更的模块（N个）：
   - ⚠️ navi-manager-bt: 12 commits (最新: 2026-06-15)
   - ⚠️ kava-clean-app: 8 commits (最新: 2026-06-14)
   - ...

   🗑️ 疑似废弃的模块（Y个）：
   - 🗑️ old-module: 项目已 archived / 超过1年无提交
   - ...

   ✅ 无变更的模块（M个）：
   - 其余模块无代码变更
   ```
6. **用户确认**：
   - "发现 X 个新增模块、N 个有变更模块、Y 个疑似废弃模块，如何处理？"
   - 用户选"全部更新" → 学习新增模块 + 更新变更模块 + 标记废弃模块
   - 用户选"跳过" → 记录到流程状态文件的待更新列表，继续版本测试
   - 用户选"只处理 XX" → 只处理指定模块
7. **增量更新**：对有变更的模块，并行启动 agent 重新学习
   - 重新读取变更后的代码
   - 对比现有知识库，找出差异点
   - 合并更新（追加新内容，不删除已有内容）
   - 在 overview.md 末尾追加"变更日志"段落
8. **新增模块学习**：对新增模块，启动完整学习流程（三文件生成）
9. **废弃模块标记**：对废弃模块，在 overview.md 顶部添加 `⚠️ 已废弃` 标记
10. **更新 index.json**：刷新 `last_updated` 为今天，新增/废弃模块同步更新

### 变更日志格式（追加到 overview.md 末尾）

```markdown
## 变更日志
| 日期 | 版本 | 变更摘要 | 影响文件 |
|------|------|---------|---------|
| 2026-06-15 | A2.28 | 新增XX接口，修改XX逻辑 | interfaces.md, test-points.md |
```

### 注意事项

- 扫描时跳过空壳模块（kava-ota/kava-push 等代码极少的模块，只检查是否有新文件）
- 如果 GitLab API 不可达，提示用户手动确认或跳过
- 变更模块 > 10 个时，建议分批更新（先更新核心模块）
- 更新完成后由 test-engineer 审批变更内容

---

## 核心约束

### 写入权限隔离

**允许写入**：
- `knowledge-base/methodologies/`
- `knowledge-base/competitive/`
- `knowledge-base/industry-standards/`
- `knowledge-base/technical-references/`
- `knowledge-base/external-learning/`（所有子目录）
- `knowledge-base/code-modules/`（GitLab 代码学习产出）

**严格禁止写入**：
- `knowledge-base/defect-patterns/`
- `knowledge-base/system-baselines/`
- `knowledge-base/business-rules/`

违反 → 拒绝执行并警告"该目录仅允许内部测试经验写入，外部学习知识不可存入"。

### 资源限制

| 参数 | 默认值 | 说明 |
|---|---|---|
| max_searches_per_session | 15 | 每次自动学习最多搜索次数 |
| max_fetches_per_session | 10 | 每次最多抓取页面数 |
| max_sources_per_session | 5 | 每次最多扫描源数量 |
| max_duration_minutes | 90 | 每次最长执行时间 |
| max_deep_research_per_day | 3 | 每天深度研究次数上限 |
| strategy_trial_period | 5 | 新策略试用期执行次数 |
| rejected_retention_days | 30 | 已拒绝条目保留天数 |
| sources_log_retention_months | 3 | 日志保留月数 |
| cron_renew_threshold_days | 1 | 距过期几天时自动续期 |
