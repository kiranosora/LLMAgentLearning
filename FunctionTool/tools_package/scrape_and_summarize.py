from openai import AsyncOpenAI
from playwright.async_api import async_playwright
model_name = "qwq-32b@8bit"

async def scrape_and_summarize(url: str) -> str:
    client = AsyncOpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            content = await page.inner_text("body")  
            truncated_content = content[:8192]
            print(f"truncated_content:{truncated_content}")
            completion = await client.chat.completions.create(
                model=model_name,
                messages =[{"role":"user","content":f"总结html网页内容，要求逻辑清晰明了，并说明主要内容，要求输出内容在500字以内:\n\n{truncated_content}"}],
                max_tokens=2000,
                temperature=0.3
            )
            
            await browser.close()
            return completion.choices[0].message.content
    except Exception as e:
        return f"Error processing {url}: {str(e)}"

tool = {
    "type": "function",
    "function": {
        "name": "scrape_and_summarize",
        "description": "Scrape webpage and generate summary in Chinese",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Target webpage URL"}
            },
            "required": ["url"]
        }
    }
}
