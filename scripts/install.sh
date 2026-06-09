#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
SKILL_DIR="$REPO_DIR/test-engineer"
SKILLS_ROOT="$HOME/.claude/skills"

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

# Step 2: 创建 symlinks
echo "[2/4] 安装 skill..."

mkdir -p "$SKILLS_ROOT"

# Skill symlink
TARGET="$SKILLS_ROOT/test-engineer"
if [ -L "$TARGET" ]; then
    rm "$TARGET"
    echo "  ✓ 已更新 skill symlink"
elif [ -d "$TARGET" ]; then
    echo "  ✗ $TARGET 已存在且不是 symlink，请手动处理"
    exit 1
fi
ln -sf "$SKILL_DIR" "$TARGET"
echo "  ✓ test-engineer → $TARGET"

# Config symlink (from repo template if not exists)
CONFIG_SRC="$REPO_DIR/config"
CONFIG_TARGET="$SKILLS_ROOT/config"
if [ -L "$CONFIG_TARGET" ]; then
    rm "$CONFIG_TARGET"
elif [ -d "$CONFIG_TARGET" ]; then
    echo "  ⚠ $CONFIG_TARGET 已存在，保留原文件"
    CONFIG_TARGET=""
fi
if [ -n "$CONFIG_TARGET" ]; then
    ln -sf "$CONFIG_SRC" "$CONFIG_TARGET"
    echo "  ✓ config → $CONFIG_TARGET"
fi

# Presets symlink
PRESETS_SRC="$REPO_DIR/presets"
PRESETS_TARGET="$SKILLS_ROOT/presets"
if [ -L "$PRESETS_TARGET" ]; then
    rm "$PRESETS_TARGET"
elif [ -d "$PRESETS_TARGET" ]; then
    echo "  ⚠ $PRESETS_TARGET 已存在，保留原文件"
    PRESETS_TARGET=""
fi
if [ -n "$PRESETS_TARGET" ]; then
    ln -sf "$PRESETS_SRC" "$PRESETS_TARGET"
    echo "  ✓ presets → $PRESETS_TARGET"
fi

echo

# Step 3: 检测私有仓库
echo "[3/4] 检测私有配置..."
PRIVATE_DIR="$(dirname "$REPO_DIR")/test-engineer-private"
if [ -d "$PRIVATE_DIR" ]; then
    echo "  ✓ 检测到 test-engineer-private"
    echo "  运行 link.sh 挂载私有配置..."
    bash "$PRIVATE_DIR/link.sh"
else
    echo "  ⚠ 未检测到 test-engineer-private（可选）"
    echo "  如需 C3/Kavabot 产品配置，请 clone test-engineer-private 到同级目录"
fi
echo

# Step 4: 生成 config.yaml
echo "[4/4] 配置..."

CONFIG_FILE="$CONFIG_SRC/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    # 检测可用 preset
    DEFAULT_PRESET="example"
    if [ -d "$PRIVATE_DIR/presets/kavabot" ]; then
        DEFAULT_PRESET="kavabot"
    fi

    read -p "  选择 preset [$DEFAULT_PRESET]: " selected_preset
    selected_preset=${selected_preset:-$DEFAULT_PRESET}

    cat > "$CONFIG_FILE" << EOF
# test-engineer 配置文件
project:
  preset: $selected_preset
EOF
    echo "  ✓ config.yaml 已生成 (preset: $selected_preset)"
else
    echo "  ✓ config.yaml 已存在，跳过"
fi

echo
echo "=============================="
echo "  安装完成！"
echo "  在 Claude Code 中输入 /test-engineer 开始使用。"
echo "=============================="
