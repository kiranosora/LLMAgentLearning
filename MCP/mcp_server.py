# server.py
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

# Create an MCP server
mcp = FastMCP("ou_mou_mcp")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
async def scrape_web_content_from_url(url: str) -> str:
    """scrape web content from url"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(proxy={"server": "http://127.0.0.1:1087"})
            page = await browser.new_page()
            await page.goto(url, timeout=120000)
            content = await page.inner_text("body")  
            truncated_content = content[:8192]
            print(f"truncated_content:{truncated_content}")
            await browser.close()
            return truncated_content
    except Exception as e:
        return f"Error processing {url}: {str(e)}"
    
@mcp.tool()
def get_memory():
    """
    Return available memory on this machine.
    """
    import psutil
    lms = 0
    mem = psutil.virtual_memory()
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_percent']):
        if proc.info['name'] == 'LM Studio Helper':
            lms = proc.info['memory_info'].rss
    print({"total_memory":f"{round(mem.total/1024/1024)}MB","free_memory":f"{round(mem.free/1024/1024)}MB"})
    return {"total_memory":f"{round(mem.total/1024/1024/1024)}GB","free_memory":f"{round(mem.free/1024/1024/1024)}GB","wired_memory":f"{round(mem.wired/1024/1024/1024)}GB","memory used by lm studio":f"{round(lms/1024/1024/1024)}GB"}

import datetime
@mcp.tool()
def get_current_local_time():
    """
    Returns the current time in local timezone in ISO format.
    """
    return {"local_time": datetime.datetime.now().isoformat()}

@mcp.tool()
def calculator(representation:str):
    """
    calculate value of the representation.
    """
    return eval(representation.replace('×','*'))

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"



if __name__ == "__main__":
    mcp.run()