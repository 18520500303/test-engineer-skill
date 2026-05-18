# test-engineer 框架内部约定

## 路径约定

SKILL.md 通过相对路径定位所有资源：

```
SKILL.md 所在目录: test-engineer/test-engineer/
├── 读配置:   Read ../config/config.yaml
├── 读模块:   Read modules/xxx.md
├── 读共享:   Read shared/definitions.md
└── 读 preset: Read ../presets/{preset}/xxx.md
```

## 模块编写规范

- 不写 YAML frontmatter（只有 SKILL.md 有）
- 第一行为 `> 数据契约见 shared/definitions.md，模块协作见 shared/interfaces.md。`
- 不引用绝对路径，用 `shared/definitions.md` 和 `../presets/{preset}/` 格式
- 不自行归档，归档由 SKILL.md 统一调 archive-manager
- 不重复调 performance-baseline IF-9（由 req-manager 统一调用）

## 加载策略

- SKILL.md 保持 500 行以内
- 模块按需 Read，不预加载
- preset 知识按话题按需加载
- 版本管理逻辑膨胀时拆到 modules/version-lifecycle.md
