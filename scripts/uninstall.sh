#!/bin/bash
set -e

TARGET="$HOME/.claude/skills/test-engineer"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$REPO_DIR/config/config.yaml"

echo "=============================="
echo "  test-engineer 卸载"
echo "=============================="
echo

# 删除 symlink
if [ -L "$TARGET" ]; then
    rm "$TARGET"
    echo "✓ 已删除 skill symlink: $TARGET"
else
    echo "- symlink 不存在，跳过"
fi

# 可选删除配置
if [ -f "$CONFIG_FILE" ]; then
    read -p "是否删除配置文件 config/config.yaml？[y/N]: " del_config
    if [ "$del_config" = "y" ] || [ "$del_config" = "Y" ]; then
        rm "$CONFIG_FILE"
        echo "✓ 已删除配置文件"
    else
        echo "- 保留配置文件"
    fi
fi

echo
echo "卸载完成。"
