import requests
base_url = "http://127.0.0.1:12345"

def test_scrae_web_content_from_url():
    url = f"{base_url}/scrape_web_content_from_url"
    data = {"url":"https://azurlane.wikiru.jp/?%E3%83%A9%E3%83%95%E3%82%A3%E3%83%BCII"}
    query_url = "https://wiki.biligame.com/blhx/%E6%8B%89%E8%8F%B2II"
    #query_url = "https://www.baidu.com"
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

test_unload_model()