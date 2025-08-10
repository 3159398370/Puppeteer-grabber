from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def get_page_source():
    # 设置Chrome选项
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 启动浏览器
    service = Service('./chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    
    # 隐藏webdriver特征
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        # 导航到页面
        driver.get('https://qlabel.tencent.com/workbench/label-tasks')
        
        print('请手动登录并导航到开始标注按钮所在页面，然后按Enter继续...')
        input()
        
        # 获取页面源码
        page_source = driver.page_source
        
        # 保存到文件
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        
        print('页面源码已保存到 page_source.html')
        
    finally:
        driver.quit()

if __name__ == "__main__":
    get_page_source()