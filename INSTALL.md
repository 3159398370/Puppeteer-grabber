# 安装指南

本文档提供详细的安装和配置步骤，帮助您快速开始使用数据标注自动化工具。

## 系统要求

### 必需组件
- **Python 3.8.10**：使用系统自带版本
- **Chrome浏览器**：用于自动化操作
- **本地chromedriver.exe**：已包含在项目中，无需额外下载
- **稳定网络连接**：用于下载依赖和API调用

## 项目结构

项目已重新组织为模块化结构：

```
Puppeteer-grabber/
├── src/                      # 源代码目录
│   ├── core/                # 核心功能模块
│   │   ├── main.py         # 主要的自动化工具类
│   │   ├── task_executor.py # 任务执行器
│   │   └── config.py       # 配置管理模块
│   └── utils/              # 工具模块
│       └── cli.py          # 命令行界面工具
├── scripts/                 # 脚本文件
│   ├── task_search.py      # 任务搜索脚本
│   ├── check_deps.py       # 依赖检查脚本
│   └── ...                 # 其他脚本
├── tests/                   # 测试文件
├── examples/                # 示例文件
├── config/                  # 配置文件
├── data/                    # 数据文件
├── run.py                   # 快速启动脚本
└── requirements.txt         # 依赖列表
```

### 支持的操作系统
- Windows 10/11
- macOS 10.14+
- Ubuntu 18.04+
- 其他Linux发行版

## 快速安装

### 方法1：使用快速启动脚本（推荐）

1. **克隆或下载项目**
   ```bash
   git clone <repository-url>
   cd Puppeteer-grabber
   ```

2. **运行快速启动脚本**
   ```bash
   python run.py
   ```
   
   脚本会自动：
   - 检查Python版本
   - 安装依赖包
   - 检查Chrome浏览器
   - 创建配置文件
   - 引导API配置
   - 启动重新组织后的模块化项目

### 方法2：手动安装

1. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   ```bash
   cp config/.env.example .env
   ```
   
   编辑 `.env` 文件，填入您的API配置。

3. **运行基础测试**
   ```bash
   python tests/test_basic.py
   ```

## 详细安装步骤

### 1. Python环境准备

#### Windows
1. 从 [Python官网](https://www.python.org/downloads/) 下载Python 3.8+
2. 安装时勾选 "Add Python to PATH"
3. 验证安装：
   ```cmd
   python --version
   pip --version
   ```

#### macOS
```bash
# 使用Homebrew安装
brew install python3

# 或使用官方安装包
# 从 https://www.python.org/downloads/ 下载
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Chrome浏览器安装

#### Windows
1. 访问 [Chrome官网](https://www.google.com/chrome/)
2. 下载并安装Chrome浏览器

#### macOS
```bash
# 使用Homebrew
brew install --cask google-chrome

# 或从官网下载安装包
```

#### Linux
```bash
# Ubuntu/Debian
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable
```

### 3. 项目依赖安装

#### 创建虚拟环境（推荐）
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 直接安装（不推荐）
```bash
pip install -r requirements.txt
```

### 4. 腾讯元宝API配置

#### 获取API密钥
1. 访问 [腾讯元宝开放平台](https://yuanbao.tencent.com)
2. 注册账号并登录
3. 创建应用
4. 获取API Key和Secret

#### 配置环境变量
1. 复制配置文件：
   ```bash
   cp config/.env.example .env
   ```

2. 编辑 `.env` 文件：
   ```env
   TENCENT_API_KEY=your_actual_api_key
   TENCENT_API_SECRET=your_actual_api_secret
   TENCENT_API_ENDPOINT=https://api.yuanbao.tencent.com
   ```

## 网络问题解决

### Chrome驱动下载失败

如果遇到 "Could not reach host" 错误：

#### 方法1：使用代理
```bash
# 设置HTTP代理
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port

# Windows
set HTTP_PROXY=http://your-proxy:port
set HTTPS_PROXY=http://your-proxy:port
```

#### 方法2：手动下载Chrome驱动
1. 查看Chrome版本：
   - 打开Chrome浏览器
   - 访问 `chrome://version/`
   - 记录版本号

2. 下载对应版本的ChromeDriver：
   - 访问 [ChromeDriver下载页](https://chromedriver.chromium.org/downloads)
   - 下载对应版本

3. 配置驱动路径：
   ```python
   # 在src/core/main.py中修改
   service = Service('/path/to/your/chromedriver')
   ```

#### 方法3：使用国内镜像
```bash
# 设置pip镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### API访问问题

#### 检查网络连接
```bash
# 测试API连通性
curl -I https://api.yuanbao.tencent.com
```

#### 配置代理（如需要）
在 `.env` 文件中添加：
```env
HTTP_PROXY=http://your-proxy:port
HTTPS_PROXY=http://your-proxy:port
```

## 验证安装

### 运行测试
```bash
python tests/test_basic.py
```

期望输出：
```
🎉 所有必需测试都通过了！工具基本功能正常。
```

### 启动工具
```bash
# 方法1：快速启动（推荐）
python run.py

# 方法2：直接启动命令行界面
python src/utils/cli.py

# 方法3：查看使用示例
python examples/example.py

# 方法4：运行特定脚本
python scripts/check_deps.py
python scripts/check_browser_status.py
```

## 常见问题

### Q1: ImportError: No module named 'selenium'
**解决方案：**
```bash
pip install selenium
# 或
pip install -r requirements.txt
```

### Q2: Chrome浏览器未找到
**解决方案：**
1. 确保Chrome已正确安装
2. 检查Chrome是否在系统PATH中
3. 尝试指定Chrome路径：
   ```python
   options.binary_location = '/path/to/chrome'
   ```

### Q3: 权限错误
**解决方案：**
```bash
# Linux/macOS
sudo chmod +x chromedriver

# 或使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### Q4: API调用失败
**解决方案：**
1. 检查API密钥是否正确
2. 确认账户余额充足
3. 检查网络连接
4. 验证API端点地址

### Q5: 中文字符显示问题
**解决方案：**
```bash
# Windows命令行
chcp 65001

# 或使用PowerShell
# 设置控制台编码为UTF-8
```

## 性能优化

### 1. 使用无头模式
在 `.env` 文件中设置：
```env
BROWSER_HEADLESS=true
```

### 2. 调整超时时间
```env
WAIT_TIMEOUT=5  # 减少等待时间
```

### 3. 批量处理优化
```env
BATCH_SIZE=5    # 减少批处理大小
DELAY_BETWEEN_TASKS=0.5  # 减少任务间延迟
```

## 卸载

### 完全卸载
```bash
# 删除虚拟环境
rm -rf venv

# 删除项目文件
rm -rf Puppeteer-grabber

# 清理pip缓存
pip cache purge
```

### 保留配置卸载
```bash
# 备份配置
cp .env .env.backup

# 删除项目文件（保留配置）
rm -rf !(*.env*|downloads)
```

## Chrome驱动配置说明

### 使用本地chromedriver.exe

项目现已配置为使用本地的 `chromedriver.exe` 文件，无需通过webdriver-manager自动下载。

**优势：**
- 启动速度更快
- 无需网络连接下载驱动
- 版本稳定可控
- 避免网络问题导致的启动失败

**配置说明：**
- chromedriver.exe 位于项目根目录
- 已在代码中配置使用本地驱动路径
- webdriver-manager 依赖已被注释，可选择性安装

**如果需要更新chromedriver：**
1. 访问 [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)
2. 下载与您的Chrome浏览器版本匹配的chromedriver
3. 替换项目根目录中的 `chromedriver.exe` 文件

## 模块导入说明

由于项目已重新组织，导入模块时需要使用新的路径：

```python
# 导入核心模块
from src.core.main import AutomationTool
from src.core.task_executor import TaskExecutor
from src.core.config import Config

# 导入工具模块
from src.utils.cli import CLI
```

## 技术支持

如果遇到安装问题：

1. **查看日志**：检查 `data/automation.log` 文件
2. **运行诊断**：执行 `python tests/test_basic.py`
3. **检查版本**：确认Python和依赖包版本
4. **Chrome驱动问题**：确认chromedriver.exe存在且与Chrome版本匹配
5. **检查项目结构**：确认文件已正确组织到相应目录
6. **提交Issue**：在项目仓库提交详细的错误信息

---

**注意**：首次运行时，Chrome驱动会自动下载，可能需要几分钟时间。请确保网络连接稳定。