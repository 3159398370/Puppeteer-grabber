import requests
from bs4 import BeautifulSoup
import json
import os
import time
import logging
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('document_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_doc_id(url):
    """从URL中提取文档ID"""
    try:
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        
        # 查找文档ID（通常是路径中的最后一个部分）
        for part in reversed(path_parts):
            if part and len(part) > 10:  # 文档ID通常比较长
                return part
        
        # 如果路径中没找到，尝试查询参数
        query_params = parse_qs(parsed_url.query)
        for key, values in query_params.items():
            if values and len(values[0]) > 10:
                return values[0]
        
        # 如果都没找到，使用整个路径作为标识
        return parsed_url.path.replace('/', '_').strip('_') or 'unknown'
        
    except Exception as e:
        logger.warning(f"提取文档ID失败: {e}")
        return 'unknown'

def crawl_document_with_selenium(url, max_retries=3, headless=True):
    """使用Selenium爬取腾讯文档内容"""
    for attempt in range(max_retries):
        driver = None
        try:
            logger.info(f"正在使用Selenium爬取文档 (尝试 {attempt + 1}/{max_retries}): {url}")
            
            # 配置Chrome选项
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 创建WebDriver实例
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.set_page_load_timeout(30)
            
            # 访问页面
            logger.info("正在访问页面...")
            driver.get(url)
            
            # 等待页面加载完成
            logger.info("等待页面加载完成...")
            time.sleep(8)  # 给页面更多时间加载
            
            # 检查是否需要登录
            login_indicators = [
                "登录", "login", "扫码", "二维码", "请先登录", "需要登录",
                "qrcode", "scan", "auth", "signin"
            ]
            
            page_text = driver.page_source.lower()
            needs_login = any(indicator in page_text for indicator in login_indicators)
            
            if needs_login:
                logger.warning("检测到页面需要登录，尝试等待更长时间...")
                time.sleep(10)
            
            # 尝试等待文档内容加载
            try:
                # 等待React应用加载完成
                WebDriverWait(driver, 30).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                # 额外等待动态内容
                time.sleep(5)
                
            except TimeoutException:
                logger.warning("页面加载超时，继续尝试获取内容")
            
            # 获取页面源码
            page_source = driver.page_source
            
            # 尝试获取页面标题
            title = driver.title
            
            # 检查页面状态
            status_info = driver.execute_script("""
                return {
                    readyState: document.readyState,
                    url: window.location.href,
                    title: document.title,
                    bodyText: document.body ? document.body.innerText.substring(0, 500) : '',
                    hasContent: document.querySelector('.smartcanvas-container, .docs-content, [role="document"]') !== null
                };
            """)
            
            logger.info(f"页面状态: {status_info}")
            
            # 尝试执行JavaScript获取更多信息
            try:
                # 尝试从window对象获取文档数据
                doc_info = driver.execute_script("""
                    try {
                        // 尝试获取基本客户端变量
                        if (window.basicClientVars && window.basicClientVars.docInfo) {
                            return {
                                type: 'basicClientVars',
                                data: window.basicClientVars.docInfo
                            };
                        }
                        
                        // 尝试获取其他可能的文档数据
                        if (window.__INITIAL_STATE__) {
                            return {
                                type: 'initialState',
                                data: window.__INITIAL_STATE__
                            };
                        }
                        
                        // 尝试获取React或Vue组件数据
                        const reactRoot = document.querySelector('[data-reactroot]');
                        if (reactRoot && reactRoot._reactInternalInstance) {
                            return {
                                type: 'react',
                                data: 'React app detected'
                            };
                        }
                        
                        return {
                            type: 'none',
                            data: 'No document data found'
                        };
                    } catch (e) {
                        return {
                            type: 'error',
                            data: e.toString()
                        };
                    }
                """)
                logger.info(f"JavaScript执行结果: {doc_info}")
                
                # 获取页面中的文本内容
                text_content = driver.execute_script("""
                    var content = document.body.innerText || document.body.textContent || '';
                    return content.trim();
                """)
                
                # 尝试获取文档特定的内容
                doc_content = driver.execute_script("""
                    // 尝试获取腾讯文档的内容
                    var selectors = [
                        '[data-testid="canvas-content"]',
                        '.docs-content',
                        '.smartcanvas-container',
                        '.canvas-container',
                        '[role="document"]',
                        '.document-content',
                        '.editor-content',
                        '.content-area',
                        '.doc-content',
                        '.main-content',
                        '.smartcanvas-content',
                        '.sc-content',
                        '[data-slate-editor="true"]'
                    ];
                    
                    var content = '';
                    for (var s = 0; s < selectors.length; s++) {
                        var elements = document.querySelectorAll(selectors[s]);
                        for (var i = 0; i < elements.length; i++) {
                            var elementText = elements[i].innerText || elements[i].textContent || '';
                            if (elementText.trim().length > 0) {
                                content += elementText + '\n';
                            }
                        }
                    }
                    return content.trim();
                """)
                
                # 检查是否有错误信息
                error_info = driver.execute_script("""
                    var errorSelectors = [
                        '.error-message',
                        '.error-info',
                        '.not-found',
                        '.access-denied',
                        '[class*="error"]',
                        '[class*="404"]',
                        '[class*="403"]'
                    ];
                    
                    var errors = [];
                    for (var s = 0; s < errorSelectors.length; s++) {
                        var elements = document.querySelectorAll(errorSelectors[s]);
                        for (var i = 0; i < elements.length; i++) {
                            var errorText = elements[i].innerText || elements[i].textContent || '';
                            if (errorText.trim().length > 0) {
                                errors.push(errorText.trim());
                            }
                        }
                    }
                    
                    // 检查常见错误文本
                    var bodyText = document.body.innerText || '';
                    var commonErrors = ['服务端故障', '文档不存在', '权限不足', '需要登录', '访问被拒绝'];
                    for (var e = 0; e < commonErrors.length; e++) {
                        if (bodyText.includes(commonErrors[e])) {
                            errors.push(commonErrors[e]);
                        }
                    }
                    
                    return errors;
                """)
                
            except Exception as js_error:
                logger.warning(f"JavaScript执行失败: {js_error}")
                text_content = ""
                doc_content = ""
                error_info = []
                doc_info = {'type': 'error', 'data': str(js_error)}
            
            logger.info(f"成功获取页面内容，标题: {title}")
            logger.info(f"文本内容长度: {len(text_content)}")
            logger.info(f"文档内容长度: {len(doc_content)}")
            if error_info:
                logger.warning(f"检测到错误信息: {error_info}")
            
            # 解析HTML
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 合并所有文本内容
            combined_content = '\n'.join(filter(None, [text_content, doc_content]))
            
            # 提取文档信息
            document_data = {
                'title': title,
                'url': url,
                'crawl_time': datetime.now().isoformat(),
                'html_content': page_source,
                'text_content': combined_content or soup.get_text(strip=True),
                'doc_content': doc_content,
                'error_info': error_info,
                'status_info': status_info,
                'needs_login': needs_login,
                'js_data': doc_info,
                'scripts': [script.get_text() for script in soup.find_all('script') if script.get_text()],
                'meta_data': {}
            }
            
            # 提取meta信息
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    document_data['meta_data'][name] = content
            
            return document_data
            
        except WebDriverException as e:
            logger.error(f"Selenium失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
            else:
                raise
        except Exception as e:
            logger.error(f"爬取失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

def crawl_document_simple(url, max_retries=3):
    """简单的requests爬取（备用方案）"""
    for attempt in range(max_retries):
        try:
            logger.info(f"正在使用requests爬取文档 (尝试 {attempt + 1}/{max_retries}): {url}")
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # 发送请求
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            logger.info(f"成功获取页面内容，状态码: {response.status_code}")
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取文档信息
            document_data = {
                'title': soup.title.string if soup.title else '',
                'url': url,
                'crawl_time': datetime.now().isoformat(),
                'html_content': response.text,
                'text_content': soup.get_text(strip=True),
                'doc_content': '',
                'additional_content': '',
                'scripts': [script.get_text() for script in soup.find_all('script') if script.get_text()],
                'meta_data': {}
            }
            
            # 提取meta信息
            for meta in soup.find_all('meta'):
                name = meta.get('name') or meta.get('property')
                content = meta.get('content')
                if name and content:
                    document_data['meta_data'][name] = content
            
            return document_data
            
        except requests.RequestException as e:
            logger.error(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
            else:
                raise
        except Exception as e:
            logger.error(f"解析失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise

def save_document(document_data, output_dir):
    """保存文档数据"""
    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        doc_id = extract_doc_id(document_data['url'])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"{doc_id}_{timestamp}"
        
        # 保存JSON文件
        json_file = os.path.join(output_dir, f"{base_filename}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(document_data, f, ensure_ascii=False, indent=2)
        logger.info(f"JSON文件已保存: {json_file}")
        
        # 保存HTML文件
        html_file = os.path.join(output_dir, f"{base_filename}.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(document_data['html_content'])
        logger.info(f"HTML文件已保存: {html_file}")
        
        # 保存纯文本文件
        if document_data.get('text_content'):
            txt_file = os.path.join(output_dir, f"{base_filename}.txt")
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(document_data['text_content'])
            logger.info(f"文本文件已保存: {txt_file}")
        
        # 如果有文档内容，单独保存
        if document_data.get('doc_content'):
            doc_file = os.path.join(output_dir, f"{base_filename}_content.txt")
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(document_data['doc_content'])
            logger.info(f"文档内容文件已保存: {doc_file}")
        
        return {
            'json_file': json_file,
            'html_file': html_file,
            'txt_file': txt_file if document_data.get('text_content') else None,
            'doc_file': doc_file if document_data.get('doc_content') else None
        }
        
    except Exception as e:
        logger.error(f"保存文件失败: {e}")
        raise

def main():
    """主函数"""
    # 腾讯文档URL
    url = "https://docs.qq.com/aio/p/scxmsn78nzsuj64?p=unUU8C3HBocfQSOGAh2BYuC"
    
    # 输出目录
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'downloads')
    
    try:
        logger.info("开始爬取腾讯文档")
        logger.info(f"目标URL: {url}")
        
        # 提取文档ID
        doc_id = extract_doc_id(url)
        logger.info(f"文档ID: {doc_id}")
        
        # 首先尝试使用Selenium爬取
        try:
            document_data = crawl_document_with_selenium(url)
            logger.info("使用Selenium成功爬取文档")
        except Exception as selenium_error:
            logger.warning(f"Selenium爬取失败: {selenium_error}")
            logger.info("回退到简单requests方式")
            document_data = crawl_document_simple(url)
        
        if not document_data:
            logger.error("无法获取文档内容")
            return
        
        # 保存文档
        saved_files = save_document(document_data, output_dir)
        
        logger.info("文档爬取完成！")
        logger.info(f"保存的文件: {saved_files}")
        
        # 输出摘要信息
        print(f"\n=== 爬取结果摘要 ===")
        print(f"文档标题: {document_data.get('title', '无标题')}")
        print(f"文档URL: {document_data['url']}")
        print(f"爬取时间: {document_data['crawl_time']}")
        print(f"文本内容长度: {len(document_data.get('text_content', ''))}")
        print(f"文档内容长度: {len(document_data.get('doc_content', ''))}")
        print(f"保存目录: {output_dir}")
        
    except Exception as e:
        logger.error(f"爬取过程中发生错误: {e}")
        raise

if __name__ == "__main__":
    main()