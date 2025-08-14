# 腾讯元宝Selenium自动化

## 概述

本项目实现了完全基于Selenium的腾讯元宝自动化功能，无需API密钥，直接通过浏览器自动化控制腾讯元宝网页版进行图片处理。

## 🚀 主要特性

- **🌐 完全基于Selenium**: 无需API密钥，直接控制腾讯元宝网页版
- **🤖 全自动处理**: 自动上传图片、发送指令、等待处理、下载结果
- **🔗 完美集成**: 与浮动控制面板无缝集成，一键调用
- **📥 智能下载**: 自动检测和下载生成的图片
- **🔄 双浏览器支持**: 支持同时操作多个浏览器实例
- **📊 实时监控**: 完整的日志记录和状态跟踪
- **🛡️ 异常处理**: 完善的错误处理和恢复机制

## 📁 文件结构

```
src/api/
├── yuanbao_client.py          # 腾讯元宝Selenium客户端
│   ├── YuanBaoClient          # 单浏览器客户端类
│   └── DualBrowserAutomation  # 双浏览器自动化管理器
│
scripts/
├── floating_control_panel.py  # 浮动控制面板（已集成）
│
tests/
├── test_selenium_yuanbao.py   # 功能测试脚本
└── demo_selenium_yuanbao.py   # 演示脚本
```

## 🔧 技术实现

### 核心组件

#### 1. YuanBaoClient 类

```python
class YuanBaoClient:
    """腾讯元宝自动化客户端"""
    
    def __init__(self, headless=False):
        # 初始化浏览器驱动和页面选择器
        
    def setup_driver(self):
        # 设置Chrome浏览器驱动
        
    def navigate_to_yuanbao(self):
        # 导航到腾讯元宝页面
        
    def upload_image(self, image_path: str) -> bool:
        # 上传图片文件
        
    def send_message(self, message: str) -> bool:
        # 发送文字指令
        
    def wait_for_response(self, timeout: int = 30) -> Optional[str]:
        # 等待处理完成
        
    def download_all_generated_images(self, save_dir: str) -> list:
        # 下载所有生成的图片
```

#### 2. DualBrowserAutomation 类

```python
class DualBrowserAutomation:
    """双浏览器自动化管理器"""
    
    def initialize(self):
        # 初始化双浏览器环境
        
    def process_task(self, image_path: str, description: str) -> bool:
        # 处理完整任务流程
        
    def download_generated_images(self, original_image_path: str) -> bool:
        # 下载处理结果
```

### 页面元素选择器

```python
selectors = {
    'chat_input': "//textarea[@placeholder='请输入您的问题']",
    'upload_button': "//button[contains(@class, 'upload-btn')]",
    'file_input': "//input[@type='file']",
    'send_button': "//button[contains(@class, 'send-btn')]",
    'response_area': "//div[contains(@class, 'message-content')]",
    'generated_image': "//img[contains(@class, 'generated-image')]",
    'loading_indicator': "//div[contains(@class, 'loading')]"
}
```

## 🎯 工作流程

### 自动化处理流程

1. **🚀 初始化浏览器**
   - 启动Chrome浏览器驱动
   - 配置浏览器选项和反检测

2. **🌐 导航到腾讯元宝**
   - 访问 https://yuanbao.tencent.com/chat
   - 检查登录状态

3. **📤 上传图片**
   - 定位文件上传按钮
   - 选择并上传图片文件
   - 等待图片预览加载

4. **📝 发送指令**
   - 在输入框中输入处理指令
   - 点击发送按钮

5. **⏳ 等待处理**
   - 监控加载指示器
   - 等待AI处理完成

6. **🖼️ 检测结果**
   - 查找生成的图片元素
   - 获取图片源地址

7. **📥 下载图片**
   - 解码Base64图片或下载URL图片
   - 保存到指定目录

8. **✅ 返回状态**
   - 记录处理日志
   - 返回操作结果

## 🛠️ 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 下载ChromeDriver

确保项目根目录有 `chromedriver.exe` 文件：

```
Puppeteer-grabber/
├── chromedriver.exe  # Chrome浏览器驱动
├── src/
├── scripts/
└── ...
```

### 3. 验证安装

```bash
python test_selenium_yuanbao.py
```

## 📖 使用方法

### 方法1: 通过浮动控制面板

1. **启动任务搜索**
   ```bash
   python scripts/task_search.py
   ```

2. **选择任务**
   - 在任务列表中选择需要处理的图片任务
   - 点击进入任务详情页面

3. **启动控制面板**
   - 按下 `p` 键启动浮动控制面板

4. **调用自动化**
   - 按下左方向键调用腾讯元宝自动化
   - 系统将自动完成整个处理流程

5. **浏览器管理**
   - **🔄 重启元宝**: 重新启动腾讯元宝浏览器（解决卡顿或异常）
   - **🔒 关闭元宝**: 安全关闭腾讯元宝浏览器
   - ⚠️ **重要**: 关闭控制面板时，腾讯元宝浏览器会继续运行

### 方法2: 直接调用API

```python
from src.automation.yuanbao_client import create_dual_browser_automation

# 创建自动化实例
automation = create_dual_browser_automation()

if automation:
    # 处理任务
    success = automation.process_task(
        image_path="path/to/image.jpg",
        description="请优化这张图片的色彩和对比度"
    )
    
    if success:
        print("处理成功！")
    
    # 关闭浏览器
    automation.close_all()
```

## 🎨 使用场景

### 图片增强
```python
description = "请帮我增强这张图片的色彩饱和度和对比度，让它看起来更加鲜艳"
```

### 风格转换
```python
description = "请将这张图片转换为油画风格，保持主体内容不变"
```

### 背景替换
```python
description = "请帮我将背景替换为蓝天白云，保持人物清晰"
```

### 图片修复
```python
description = "请帮我修复这张老照片的划痕和褪色问题"
```

## 🔍 测试和调试

### 运行测试

```bash
# 功能测试
python test_selenium_yuanbao.py

# 演示脚本
python demo_selenium_yuanbao.py
```

### 调试模式

```python
# 启用可视化模式（非无头模式）
client = YuanBaoClient(headless=False)
```

### 日志查看

日志文件位置：`yuanbao_automation.log`

```bash
tail -f yuanbao_automation.log
```

## ⚙️ 配置选项

### 浏览器配置

```python
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')
```

### 等待时间配置

```python
self.wait = WebDriverWait(self.driver, 10)  # 默认等待10秒
```

### 下载目录配置

```python
save_dir = os.path.join(base_dir, 'yuanbao_results')  # 默认保存目录
```

## 🚨 注意事项

1. **浏览器持久化运行**: ⚠️ **腾讯元宝浏览器需要保持开启状态，不能随意关闭**
   - 浮动控制面板关闭时，腾讯元宝浏览器会继续运行
   - 这是为了保持登录状态和处理会话的连续性
   - 如需关闭，请使用面板中的"🔒 关闭元宝"按钮
   - 可使用"🔄 重启元宝"按钮重新启动浏览器

2. **登录要求**
   - 首次使用需要手动登录腾讯元宝
   - 系统会自动检测登录状态

3. **网络要求**
   - 需要稳定的网络连接
   - 确保能正常访问腾讯元宝网站

4. **浏览器版本**
   - 确保Chrome浏览器版本与ChromeDriver匹配
   - 建议使用最新版本

5. **处理时间**
   - AI处理时间因图片复杂度而异
   - 系统会自动等待处理完成

## 🔧 故障排除

### 常见问题

1. **ChromeDriver版本不匹配**
   ```
   解决方案：下载与Chrome浏览器版本匹配的ChromeDriver
   ```

2. **元素定位失败**
   ```
   解决方案：检查页面选择器是否需要更新
   ```

3. **登录状态丢失**
   ```
   解决方案：重新手动登录腾讯元宝
   ```

4. **图片下载失败**
   ```
   解决方案：检查网络连接和保存目录权限
   ```

## 📈 性能优化

1. **使用无头模式**
   ```python
   client = YuanBaoClient(headless=True)
   ```

2. **调整等待时间**
   ```python
   self.wait = WebDriverWait(self.driver, 5)  # 减少等待时间
   ```

3. **批量处理**
   ```python
   # 复用浏览器实例处理多个任务
   for task in tasks:
       automation.process_task(task['image'], task['description'])
   ```

## 🔮 未来扩展

- [ ] 支持更多图片格式
- [ ] 添加批量处理功能
- [ ] 实现处理进度监控
- [ ] 支持自定义选择器配置
- [ ] 添加处理结果评估
- [ ] 实现智能重试机制

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

---

**🎉 享受全自动的腾讯元宝图片处理体验！**