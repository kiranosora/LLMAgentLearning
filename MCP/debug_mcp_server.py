import requests
url = "http://127.0.0.1:12345/scrape_web_content_from_url"
data = {"url":"https://azurlane.wikiru.jp/?%E3%83%A9%E3%83%95%E3%82%A3%E3%83%BCII"}
query_url = "https://wiki.biligame.com/blhx/%E6%8B%89%E8%8F%B2II"
#query_url = "https://www.baidu.com"
data = {"url":query_url}
response = requests.post(url, json=data)
print(f"response:{response}")
print(f"response.text: {response.text}")