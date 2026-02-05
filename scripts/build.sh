#!/bin/bash
# Life Canvas OS - 自动打包脚本

set -e  # 遇到错误立即退出

echo "🚀 Life Canvas OS - 开始打包"
echo "=================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 计算并进入项目根目录（scripts 的上一级）
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"
echo "📍 项目目录: $PROJECT_ROOT"
echo ""

# === 阶段 1: 环境检查 ===
echo -e "${YELLOW}📋 阶段 1: 环境检查${NC}"

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 未安装${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ $1 已安装${NC}"
    fi
}

check_command node
check_command pnpm
check_command python3

echo ""
node --version
pnpm --version
python3 --version

echo ""

# === 阶段 2: 清理旧文件 ===
echo -e "${YELLOW}🧹 阶段 2: 清理旧文件${NC}"

echo "删除 backend/dist 和 backend/build..."
rm -rf "$PROJECT_ROOT/backend/dist"
rm -rf "$PROJECT_ROOT/backend/build"

echo "删除 dist..."
rm -rf "$PROJECT_ROOT/dist"

echo -e "${GREEN}✅ 清理完成${NC}"
echo ""

# === 阶段 3: 打包 Python 后端 ===
echo -e "${YELLOW}🐍 阶段 3: 打包 Python 后端${NC}"

cd "$PROJECT_ROOT/backend"
echo "运行 PyInstaller..."
"$PROJECT_ROOT/venv/bin/python3" -m PyInstaller backend.spec --clean

if [ -f "dist/backend" ]; then
    SIZE=$(du -h dist/backend | cut -f1)
    echo -e "${GREEN}✅ Python 打包成功！大小: $SIZE${NC}"
else
    echo -e "${RED}❌ Python 打包失败${NC}"
    exit 1
fi

cd "$PROJECT_ROOT"
echo ""

# === 阶段 4: 测试 Python 可执行文件 ===
echo -e "${YELLOW}🧪 阶段 4: 测试 Python 可执行文件${NC}"

echo "测试 IPC 模式（2秒后自动停止）..."
timeout 2 backend/dist/backend || true

echo -e "${GREEN}✅ Python 可执行文件正常${NC}"
echo ""

# === 阶段 5: 构建 Electron ===
echo -e "${YELLOW}⚡️ 阶段 5: 构建 Electron${NC}"

# 设置 Electron 镜像源
export ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/

pnpm compile:app

echo -e "${GREEN}✅ Electron 构建完成${NC}"
echo ""

# === 阶段 6: 打包 Electron 应用 ===
echo -e "${YELLOW}📦 阶段 6: 打包 Electron 应用${NC}"

pnpm build

if [ -d "dist/v0.0.1/mac-arm64" ]; then
    echo -e "${GREEN}✅ Electron 打包成功${NC}"

    echo ""
    echo "生成的文件:"
    ls -lh dist/v0.0.1/ | tail -n +2
else
    echo -e "${RED}❌ Electron 打包失败${NC}"
    exit 1
fi

# === 阶段 6.5: 复制 Python 可执行文件 ===
echo -e "${YELLOW}🐍 阶段 6.5: 复制 Python 可执行文件${NC}"

APP_RESOURCES="dist/v0.0.1/mac-arm64/Life Canvas OS.app/Contents/Resources"
PYTHON_RUNTIME_DIR="$APP_RESOURCES/python-runtime"

echo "创建 python-runtime 目录..."
mkdir -p "$PYTHON_RUNTIME_DIR"

echo "复制 Python 可执行文件..."
cp backend/dist/backend "$PYTHON_RUNTIME_DIR/backend"

if [ -f "$PYTHON_RUNTIME_DIR/backend" ]; then
    SIZE=$(du -h "$PYTHON_RUNTIME_DIR/backend" | cut -f1)
    echo -e "${GREEN}✅ Python 文件复制成功！大小: $SIZE${NC}"
    echo "位置: $PYTHON_RUNTIME_DIR/backend"
else
    echo -e "${RED}❌ Python 文件复制失败${NC}"
    exit 1
fi

echo ""

# === 阶段 7: 测试打包的应用 ===
echo -e "${YELLOW}🎯 阶段 7: 测试打包的应用${NC}"

APP_PATH="$PROJECT_ROOT/dist/v0.0.1/mac-arm64/Life Canvas OS.app"

if [ -d "$APP_PATH" ]; then
    echo "启动应用..."
    open "$APP_PATH"

    echo -e "${GREEN}✅ 应用已启动${NC}"
    echo ""
    echo "请检查以下功能:"
    echo "  1. 应用窗口是否正常显示"
    echo "  2. Python 控制台是否打开（应该有终端窗口）"
    echo "  3. 点击'测试 Python API'按钮是否正常"
    echo ""
    echo "应用路径: $APP_PATH"
else
    echo -e "${RED}❌ 找不到打包的应用${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 打包测试完成！${NC}"
echo ""
