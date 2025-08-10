import requests
import json

def get_page_source_with_requests():
    url = "https://qlabel.tencent.com/workbench/label-tasks/1151687496995192832"
    
    # 设置请求头，模拟浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print(f"正在获取页面源码: {url}")
        # 禁用代理
        proxies = {
            'http': None,
            'https': None,
        }
        response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            # 保存HTML源码
            with open('page_source_requests.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("✅ 页面源码已保存到 page_source_requests.html")
            
            # 分析页面内容
            content = response.text
            print(f"\n页面内容长度: {len(content)} 字符")
            
            # 查找开始标注相关的内容
            if '开始标注' in content:
                print("✅ 页面包含'开始标注'文本")
                # 查找包含开始标注的行
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if '开始标注' in line:
                        print(f"第{i+1}行: {line.strip()}")
            else:
                print("❌ 页面不包含'开始标注'文本")
                
            # 查找button标签
            if '<button' in content:
                print("\n✅ 页面包含button标签")
                import re
                buttons = re.findall(r'<button[^>]*>.*?</button>', content, re.DOTALL)
                print(f"找到 {len(buttons)} 个button标签")
                for i, button in enumerate(buttons[:10]):  # 只显示前10个
                    print(f"Button {i+1}: {button[:200]}...")
            else:
                print("❌ 页面不包含button标签")
                
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

if __name__ == "__main__":
    get_page_source_with_requests()