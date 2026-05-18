# 性能基线指标定义

本文件定义了商用清洁机器人性能基线的所有可选指标、测量方法、样本量要求和判定标准。

建立基线时，按产品实际情况选择需要的指标，不必全部填写。

---

## 清洁性能 (cleaning)

| 指标key | 中文名 | 单位 | 方向 | 样本量 | 测试方法 | 默认判定标准 | 标准来源 |
|---------|--------|------|------|--------|---------|-------------|---------|
| dust_removal_rate | 硬地板除尘率 | % | higher_better | ≥3次 | 标准灰尘50g/m²，3次取均值 | ≥70% | GB/T 46495-2025 |
| carpet_dust_removal_rate | 地毯除尘率 | % | higher_better | ≥3次 | 标准细砂100g/m²，3次取均值 | ≥60%（内部） | - |
| coverage_rate | 清洁覆盖率 | % | higher_better | ≥3次 | 标准场景(≥15m²)路径日志分析 | ≥95%（内部） | - |
| edge_cleaning_rate | 边角除尘率 | % | higher_better | ≥3次 | 沿墙50mm带状区域 | ≥65% | QB/T 4833-2022 |
| cleaning_efficiency | 清洁效率 | m²/h | higher_better | ≥3次 | 满电标准模式连续运行 | 产品规格值±10% | GB/T 46495-2025 |
| path_repeat_rate | 路径重复率 | % | lower_better | ≥3次 | 路径日志分析 | ≤5% | - |

## 导航性能 (navigation)

| 指标key | 中文名 | 单位 | 方向 | 样本量 | 测试方法 | 默认判定标准 | 标准来源 |
|---------|--------|------|------|--------|---------|-------------|---------|
| mapping_accuracy | 建图精度 | mm | lower_better | 1次(≥10参考点) | ≥10参考点≥15对距离 | ≤50mm | TAIIA001-2020 |
| mapping_completeness | 建图完整性 | % | higher_better | ≥3次 | 建图面积/实际面积 | ≥95% | TAIIA001-2020 |
| positioning_repeatability | 定位重复精度 | mm | lower_better | 30次 | 同一点30次到达偏差(2σ) | ≤30mm | TAIIA001-2020 |
| path_tracking_error | 路径跟踪误差 | mm | lower_better | ≥5次 | 标准路径(直线/L/U形) | ≤100mm | TAIIA001-2020 |
| docking_success_rate | 回桩成功率 | % | higher_better | ≥30次 | 不同距离和角度 | ≥99% | - |
| navigation_success_rate | 导航成功率 | % | higher_better | ≥20次 | 标准场景导航到目标点 | ≥99% | TAIIA001-2020 |

## 续航能耗 (energy)

| 指标key | 中文名 | 单位 | 方向 | 样本量 | 测试方法 | 默认判定标准 | 标准来源 |
|---------|--------|------|------|--------|---------|-------------|---------|
| runtime | 续航时间 | min | higher_better | ≥3次 | 满电标准模式连续运行 | 产品规格值±10% | GB/T 46495-2025 |
| charge_time | 充电时间 | min | lower_better | ≥3次 | 0%→100% | 产品规格值±10% | GB/T 46495-2025 |
| standard_power | 标准模式功耗 | W | lower_better | ≥3次 | 功率计实时测量取均值 | 记录（无通用标准） | - |
| standby_power | 待机功耗 | W | lower_better | ≥3次 | 功率计测量 | ≤5W | - |

## 安全指标 (safety)

| 指标key | 中文名 | 单位 | 方向 | 样本量 | 测试方法 | 默认判定标准 | 标准来源 |
|---------|--------|------|------|--------|---------|-------------|---------|
| collision_force | 碰撞力 | N | lower_better | ≥10次 | 拉力传感器 | ≤10N | - |
| emergency_stop_time | 急停响应时间 | ms | lower_better | ≥10次 | 高速摄影/日志 | ≤500ms | - |
| fall_prevention_rate | 防跌落成功率 | % | higher_better | ≥30次 | 台面边缘测试 | 100% | GB/T 46495-2025 |
| obstacle_detection_rate | 避障识别率 | % | higher_better | ≥100次 | 标准障碍物库 | ≥99% | TAIIA001-2020 |

## 运动控制 (motion)

| 指标key | 中文名 | 单位 | 方向 | 样本量 | 测试方法 | 默认判定标准 | 标准来源 |
|---------|--------|------|------|--------|---------|-------------|---------|
| linear_tracking_accuracy | 直线跟踪精度 | mm | lower_better | ≥10次 | 沿标准直线路径测横向偏差 | ≤30mm | GB/T 40327-2021 |
| turn_accuracy | 转弯角度精度 | ° | lower_better | ≥10次 | 90°/180°转弯后角度偏差 | ≤3° | GB/T 40327-2021 |
| speed_accuracy | 速度控制精度 | % | lower_better | ≥5次 | 设定速度vs实际速度偏差 | ≤5% | GB/T 40327-2021 |
| braking_distance | 制动距离 | mm | lower_better | ≥10次 | 标准速度到完全停止 | 按速度分级 | - |

---

## 自定义指标

用户可以添加不在上述列表中的自定义指标，需提供：
- `key`：英文标识符（小写+下划线）
- `name`：中文名称
- `unit`：单位
- `direction`：higher_better 或 lower_better
- `pass_criteria`：判定标准
- `min_samples`：最少样本量
