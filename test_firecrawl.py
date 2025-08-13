import requests
import json

# Firecrawl服务地址
firecrawl_url = "http://localhost:3002/v0/scrape"

# 测试数据
payload = {
    "url": "https://www.modelscope.cn/models/Wan-AI/Wan2.2-T2V-A14B",
    "formats": ["markdown"]
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(firecrawl_url, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        print("爬取成功!")
        print(f"状态: {result.get('success')}")
        print(f"数据: {result.get('data', {}).get('markdown', 'No markdown content')}")
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")

except Exception as e:
    print(f"请求过程中发生错误: {e}")