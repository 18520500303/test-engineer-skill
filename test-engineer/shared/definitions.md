# 测试体系公共定义

> 本文件是测试体系 Skills 的**唯一权威定义源**。各 Skill 引用本文件而非重复定义。
> 修改本文件即全局生效，无需逐个 Skill 同步。

---

## 一、JSON 测试数据格式（TD-Test Data v1.0）

所有测试数据文件必须遵循此格式。

### Schema

```json
{
  "version": "1.0",
  "info": {
    "version_code": "A2.14",
    "requirement_id": "REQ-A214-001",
    "requirement_name": "悬空障碍物碰撞优化",
    "test_date": "",
    "tester": ""
  },
  "test_cases": [
    {
      "case_id": "TC-001",
      "case_name": "悬空障碍物避障测试",
      "module": "避障模块",
      "priority": "P0",
      "test_points": ["SC-001", "SC-002"],
      "status": "pending",
      "result": "",
      "execution_time": "",
      "preconditions": "",
      "test_steps": "",
      "expected_results": "",
      "tags": "",
      "edit_mode": "STEP",
      "remarks": ""
    }
  ],
  "statistics": {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "pass_rate": 0
  }
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|:----:|:----:|------|
| version | string | Y | 数据格式版本，固定"1.0" |
| info.version_code | string | Y | 版本号 |
| info.requirement_id | string | Y | 需求ID |
| info.requirement_name | string | Y | 需求名称 |
| info.test_date | string | - | 测试日期（执行时填写） |
| info.tester | string | - | 测试人员（执行时填写） |
| test_cases.case_id | string | Y | 用例ID，格式TC-001 |
| test_cases.case_name | string | Y | 用例名称 |
| test_cases.module | string | - | 所属模块 |
| test_cases.priority | string | Y | 优先级 P0/P1/P2/P3 |
| test_cases.test_points | array | - | 关联的测试点ID列表 |
| test_cases.status | string | Y | pending/passed/failed/skipped |
| test_cases.result | string | - | 测试结果描述 |
| test_cases.execution_time | string | - | 执行时间 |
| test_cases.preconditions | string | - | 前置条件 |
| test_cases.test_steps | string | - | 测试步骤 |
| test_cases.expected_results | string | - | 预期结果 |
| test_cases.tags | string | - | 标签 |
| test_cases.edit_mode | string | - | 编辑模式 |
| test_cases.remarks | string | - | 备注 |
| statistics.total | number | Y | 总用例数（=test_cases数组长度） |
| statistics.passed | number | Y | 通过数 |
| statistics.failed | number | Y | 失败数 |
| statistics.skipped | number | Y | 跳过数 |
| statistics.pass_rate | number | Y | 通过率（百分比，精确到小数点后1位） |

### 初始状态规则

- 所有 test_cases 的 status 必须为 "pending"
- result、execution_time、tester、test_date 为空字符串
- statistics.total = test_cases 数组长度
- passed/failed/skipped = 0，pass_rate = 0

### 文件命名

- 测试数据模板：`{需求名称}_test_data_template.json`
- 测试数据文件：`{需求名称}_test_data.json`

---

## 二、需求ID命名规则

| 需求类型 | 格式 | 示例 |
|----------|------|------|
| 算法线 | `REQ-A{版本号去点}-{三位序号}` | REQ-A214-001 |
| 平台线 | `REQ-PLAT{版本主标识}-{三位序号}` | REQ-PLAT26-001 |
| 专项测试 | `REQ-SPECIAL-{专项名称}-{三位序号}` | REQ-SPECIAL-移动速度优化-001 |

### 方案ID

| 格式 | 示例 |
|------|------|
| `PLAN-A{版本号去点}-{三位序号}` | PLAN-A214-001 |

---

## 三、优先级定义

| 优先级 | 说明 |
|:------:|------|
| P0 | 核心功能，必须实现/验证 |
| P1 | 重要功能，影响用户体验 |
| P2 | 一般优化功能 |
| P3 | 低优先级优化 |

---

## 四、需求状态定义

| 状态 | 说明 |
|------|------|
| 待实现 | 需求已记录，尚未开始 |
| 实现中 | 正在开发中 |
| 已实现 | 功能已开发完成 |
| 已验证 | 测试验证通过 |

---

## 五、需求文档模板

### 算法线需求

```markdown
# REQ-A{版本}-{序号} {需求名称}

## 基本信息
| 字段 | 内容 |
|------|------|
| 需求ID | REQ-A{版本}-{序号} |
| 关联版本 | {版本号} |
| 优先级 | {P0/P1/P2/P3} |
| 创建日期 | {YYYY-MM-DD} |
| 状态 | 待实现 |

## 需求背景
[问题场景、用户反馈]

## 需求描述
[功能需求、核心机制]

## 技术要求
| 序号 | 要求项 | 指标/说明 |
|------|--------|-----------|
| 1 | {要求项} | {指标} |

## 验收标准
| 验收项 | 标准 |
|--------|------|
| {验收项} | {标准} |

## 关联测试点
- {测试点1}
- {测试点2}

## 关联方案
- PLAN-A{版本}-{序号}: {方案名称}

## 基线采集指标
| # | 指标 | 单位 | 采集方法 | 最少样本量 | 当前基准值 | 判定标准 |
|---|------|------|---------|-----------|-----------|---------|
| 1 | {指标名} | {单位} | {方法} | {次数} | {基准值或"首次采集"} | {标准} |

> 注：基线指标由 performance-baseline 根据需求类型自动推荐。

## 变更历史
| 日期 | 变更内容 | 变更人 |
|------|----------|--------|
| {YYYY-MM-DD} | 创建需求 | {姓名} |
```

### 平台线需求

```markdown
# REQ-PLAT{版本}-{序号} {需求名称}

## 基本信息
| 字段 | 内容 |
|------|------|
| 需求ID | REQ-PLAT{版本}-{序号} |
| 关联版本 | {版本号} |
| Jira Key | {WRB-xxxxx 或 无} |
| 优先级 | {P0/P1/P2/P3} |
| 模块 | {模块名称} |
| 创建日期 | {YYYY-MM-DD} |
| 状态 | 待实现 |

## 需求来源
- 来源：{Jira 导入 / 手动创建}
- 原始链接：{https://jira.cvte.com/browse/WRB-xxxxx 或 无}

## 需求背景
[用户痛点、业务需求]

## 需求描述
[功能需求、交互流程]

## 功能要求
- [ ] 要求1
- [ ] 要求2

## 验收标准
| 验收项 | 标准 |
|--------|------|
| {验收项} | {标准} |

## 关联测试用例
- {测试用例1}
- {测试用例2}

## 基线采集指标
| # | 指标 | 单位 | 采集方法 | 最少样本量 | 当前基准值 | 判定标准 |
|---|------|------|---------|-----------|-----------|---------|
| 1 | {指标名} | {单位} | {方法} | {次数} | {基准值或"首次采集"} | {标准} |

> 注：基线指标由 performance-baseline 根据需求类型自动推荐。
```

---

## 六、版本号格式规范

| 版本类型 | 格式 | 示例 | 版本线 |
|----------|------|------|--------|
| 算法版本 | A2.xx | A2.14, A2.27 | 算法线 |
| 控制版本 | V7.x.x | V7.1.0 | 算法线 |
| 平台版本 | v1.xx / MP_vX.X.X | v1.1.26, MP_v1.1.27 | 平台线 |

---

## 七、Jira 项目映射

> Jira 项目映射是**产品特有数据**，不在共享定义层定义。
> 各产品 preset 在 `{paths.jira_mapping}` 中维护自己的 Jira 项目映射。
>
> 使用 JQL 查询时，通过 preset 中的 `jira_projects.*` 变量引用项目名称，
> 不要硬编码 Jira 项目名（如 WRB、RBTPROJECT）。

---

## 八、文件输出根目录

所有测试文档输出到：`{output.root}`

> 此值由 preset 的 `paths.output_root` 定义（如 c3-commercial 默认为 `~/Desktop/workdata/测试`）。
> 换产品或换机器时只需修改 preset，无需逐个文件更新。

### 目录结构

```
{output.root}/
├── 算法/
│   ├── {版本}/
│   │   ├── 需求/
│   │   ├── 测试点/
│   │   ├── 测试数据/
│   │   ├── 方案/
│   │   ├── 测试用例/
│   │   ├── 测试报告/
│   │   ├── 专项/
│   │   └── 归档/
│   └── 跨版本专项/
├── 平台/
│   ├── {版本}/
│   │   ├── 需求/
│   │   ├── 测试数据/
│   │   ├── 测试用例/
│   │   ├── 测试报告/
│   │   └── 归档/
│   ├── _共享/
│   │   └── 需求记录.md
│   └── 测试用例_{版本}.xlsx
├── 专项/{专项名称}/
├── _知识库/
│   └── 性能基线/reports/
└── 学习报告/
```

---

## 九、报告通用约束

- **署名**：周健荣
- **日期格式**：YYYY-MM-DD
- **报告结论**：必须查 Jira 缺陷数据后再下结论，不能只看用例通过率
- **术语**：用"软件版本"或"模块应用"替代"固件"
- **环境信息**：用实际值，不照搬方案计划值，主动确认版本号

---

> 模块协作关系和接口定义见 `shared/interfaces.md`。
