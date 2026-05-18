#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
SKILL_DIR="$REPO_DIR/test-engineer"
CONFIG_DIR="$REPO_DIR/config"
PRESETS_DIR="$REPO_DIR/presets"
TARGET="$HOME/.claude/skills/test-engineer"

echo "=============================="
echo "  test-engineer 安装向导"
echo "=============================="
echo

# Step 1: 检测 Claude Code
echo "[1/4] 检测 Claude Code 环境..."
if [ ! -d "$HOME/.claude" ]; then
    echo "  ✗ 未检测到 Claude Code（~/.claude/ 不存在）"
    echo "  请先安装 Claude Code: https://claude.ai/code"
    exit 1
fi
echo "  ✓ Claude Code 已安装"
echo

# Step 2: 选择 preset
echo "[2/4] 选择业务配置包:"
PRESETS=()
i=1
for d in "$PRESETS_DIR"/*/; do
    name=$(basename "$d")
    PRESETS+=("$name")
    if [ "$name" = "example" ]; then
        echo "  $i) $name (示例)"
    else
        echo "  $i) $name"
    fi
    i=$((i + 1))
done
echo "  $i) 自定义路径"
echo
read -p "请选择 [1]: " preset_choice
preset_choice=${preset_choice:-1}

if [ "$preset_choice" -le "${#PRESETS[@]}" ] 2>/dev/null; then
    SELECTED_PRESET="${PRESETS[$((preset_choice - 1))]}"
else
    read -p "请输入 preset 目录路径: " custom_path
    SELECTED_PRESET="custom"
fi
echo "  已选择: $SELECTED_PRESET"
echo

# Step 3: 配置基本信息
echo "[3/4] 配置基本信息:"

read -p "  姓名: " user_name
read -p "  Jira 用户名: " jira_username
read -p "  文件输出目录 [~/Desktop/workdata/测试用例]: " output_root
output_root=${output_root:-"~/Desktop/workdata/测试用例"}

# 从 preset.yaml 读取产品名（如果有）
product_name=""
if [ -f "$PRESETS_DIR/$SELECTED_PRESET/preset.yaml" ]; then
    product_name=$(grep "display_name:" "$PRESETS_DIR/$SELECTED_PRESET/preset.yaml" | sed 's/.*: *"\(.*\)"/\1/' 2>/dev/null || echo "")
fi
if [ -z "$product_name" ]; then
    read -p "  产品名称: " product_name
fi

read -p "  Jira 主机 [jira.cvte.com]: " jira_host
jira_host=${jira_host:-"jira.cvte.com"}

read -p "  Confluence 主机 [kb.cvte.com]: " confluence_host
confluence_host=${confluence_host:-"kb.cvte.com"}

# 从 preset.yaml 读取 Jira 项目（如果有默认值）
read -p "  平台线 Jira 项目 [WRB]: " platform_project
platform_project=${platform_project:-"WRB"}

read -p "  算法线 Jira 项目 [RBTPROJECT]: " algorithm_project
algorithm_project=${algorithm_project:-"RBTPROJECT"}

echo

# Step 4: 安装
echo "[4/4] 安装中..."

# 创建 symlink
if [ -L "$TARGET" ]; then
    rm "$TARGET"
    echo "  已移除旧 symlink"
fi
if [ -d "$TARGET" ]; then
    echo "  ✗ $TARGET 已存在且不是 symlink，请手动处理"
    exit 1
fi
ln -s "$SKILL_DIR" "$TARGET"
echo "  ✓ skill symlink → $TARGET"

# 生成 config.yaml
cat > "$CONFIG_DIR/config.yaml" << EOF
project:
  name: "$product_name"
  preset: "$SELECTED_PRESET"

user:
  name: "$user_name"
  jira_username: "$jira_username"

jira:
  host: "$jira_host"
  platform_project: "$platform_project"
  algorithm_project: "$algorithm_project"
  version_field: "affectedVersion"

output:
  root: "$output_root"

confluence:
  host: "$confluence_host"

metersphere:
  enabled: false
EOF
echo "  ✓ 配置写入 → config/config.yaml"

echo
echo "=============================="
echo "  安装完成！"
echo "  在 Claude Code 中输入 /test-engineer 开始使用。"
echo "=============================="
