import requests
base_url = "http://127.0.0.1:12345"

def test_scrae_web_content_from_url():
    url = f"{base_url}/scrape_web_content_from_url"
    url = f"{base_url}/scrape_with_firecrawl"
    data = {"url":"https://azurlane.wikiru.jp/?%E3%83%A9%E3%83%95%E3%82%A3%E3%83%BCII"}
    query_url = "https://wiki.biligame.com/blhx/%E6%8B%89%E8%8F%B2II"
    query_url = "https://finance.sina.com.cn/stock/usstock/c/2025-04-06/doc-inesefte2954625.shtml"
    #query_url = "https://www.baidu.com"
    #query_url = "https://www.spacex.com/"
    data = {"url":query_url}
    response = requests.post(url, json=data)
    print(f"response:{response}")
    print(f"response.text: {response.text}")

def test_unload_model():
    url = f"{base_url}/unload_model"
    model_path = "qwen2.5-0.5b-instruct-mlx"
    #query_url = "https://www.baidu.com"
    data = {"model_path":model_path}
    response = requests.post(url, json=data)
    print(f"response:{response}")
    print(f"response.text: {response.text}")

def test_add():
    url = f"{base_url}/add"
    #query_url = "https://www.baidu.com"
    data = {"num1": 1, "num2": 1}
    response = requests.post(url, json=data)
    print(f"response:{response}")
    print(f"response.text: {response.text}")

#test_unload_model()
test_scrae_web_content_from_url()

from playwright.async_api import async_playwright

async def scrape_web_content_from_url(url: str) -> str:
    """scrape web content from url"""
    try:
        async with async_playwright() as p:
            print(f"start browser")
            browser = await p.chromium.launch(proxy={"server": "http://127.0.0.1:1087"}, headless=False)
            print("start new_page")
            page = await browser.new_page()
            await page.goto(url, timeout=120000)
            content = await page.inner_text("body")  
            truncated_content = content[:8192*4]
            print(f"truncated_content:{truncated_content}")
            await browser.close()
            return truncated_content
    except Exception as e:
        return f"Error processing {url}: {str(e)}"
 

query_url = "https://finance.sina.com.cn/stock/usstock/c/2025-04-06/doc-inesefte2954625.shtml"
query_url = "https://wiki.biligame.com/blhx/%E6%8B%89%E8%8F%B2II"
query_url = "https://azurlane.wikiru.jp/?%E3%83%A9%E3%83%95%E3%82%A3%E3%83%BCII"
import asyncio
#asyncio.run(scrape_web_content_from_url(query_url))
#test_add()

def test_dl():
    data = {"model_path":""}


def test_extract_pdf():
    url = f"{base_url}/download_and_extract_pdf"
    data = {"url":"https://arxiv.org/pdf/2505.22735"}
    response = requests.post(url, json=data)
    print(f"response:{response}")
    print(f"response.text: {response.text}")
