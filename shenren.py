import requests
import time
from bs4 import BeautifulSoup
import json

# 基础URL
base_url = "https://www.12371.cn/special/cidian/dnfg/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_article_links(base_url):
    """
    从专题页获取所有文章链接，过滤掉index.shtml，只保留*.shtml
    """
    print("正在获取文章链接列表...")
    response = requests.get(base_url, headers=headers)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有符合条件的a标签
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        # 只保留shtml文件，且不是index.shtml
        if href.endswith('.shtml') and 'index.shtml' not in href:
            if href not in links:
                links.append(href)
    
    print(f"共找到 {len(links)} 个文章链接")
    return links

def get_article_content(url):
    """
    获取单个文章页面的标题和内容
    标题：<h4 class="dyw1027new-catalogue-title">
    内容：<div class="dyw1027new-catalogue-content">
    """
    try:
        print(f"  正在抓取: {url}")
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取标题
        title_elem = soup.find('h4', class_='dyw1027new-catalogue-title')
        title = title_elem.get_text(strip=True) if title_elem else "未找到标题"
        
        # 提取内容
        content_elem = soup.find('div', class_='dyw1027new-catalogue-content')
        # 获取内容中的所有文本，保留格式
        content = content_elem.get_text(strip=True) if content_elem else "未找到内容"
        
        # 清理标题中可能包含的注释标记
        title = title.replace('<!--repaste.title.begin-->', '').replace('<!--repaste.title.end-->', '').strip()
        
        return {
            'url': url,
            'title': title,
            'content': content
        }
    except Exception as e:
        print(f"  抓取失败 {url}: {str(e)}")
        return None

def crawl_all_articles():
    """
    主函数：爬取所有文章
    """
    # 1. 获取所有文章链接
    article_links = get_article_links(base_url)
    
    # 2. 逐个爬取文章内容
    all_articles = []
    for i, link in enumerate(article_links, 1):
        print(f"\n[{i}/{len(article_links)}]")
        article = get_article_content(link)
        if article:
            all_articles.append(article)
        # 添加延时，避免请求过快
        time.sleep(0.5)
    
    # 3. 保存结果
    with open('articles.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n爬取完成！共获取 {len(all_articles)} 篇文章，已保存到 articles.json")
    return all_articles

if __name__ == "__main__":
    articles = crawl_all_articles()
    
    # 打印前几篇文章预览
    print("\n=== 文章预览 ===")
    for article in articles[:3]:
        print(f"标题: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"内容预览: {article['content'][:100]}...")
        print("-" * 50)