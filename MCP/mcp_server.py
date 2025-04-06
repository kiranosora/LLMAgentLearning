# server.py
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright
import json

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
def list_large_models() -> dict:
    """List large models which can be used as an inference model via lms ps command (JSON format)"""
    import subprocess
    import json
    try:
        result = subprocess.run(["lms", "ps", "--json"], capture_output=True, text=True, check=True)
        obj = json.loads(result.stdout)
        for model_info in obj:
            model_size = model_info.pop("sizeBytes", None)
            if model_size != None:
                model_size = model_size /1024/1024/1024
                model_info["sizeGB"] = model_size
        return {"output": obj}
    except Exception as e:
        return {"error": f"Failed to list models: {str(e)}"}

# New tool for listing downloaded models
@mcp.tool()
def list_downloaded_models() -> dict:
    """List all downloaded models via lms ls --json (machine-readable format)"""
    import subprocess
    try:
        result = subprocess.run(["lms", "ls", "--json"], capture_output=True, text=True, check=True)
        obj = json.loads(result.stdout)
        for model_info in obj:
            model_size = model_info.pop("sizeBytes", None)
            if model_size != None:
                model_size = model_size /1024/1024/1024
                model_info["sizeGB"] = model_size
        return {"output": obj}
    except Exception as e:
        return {"error": f"Command failed: {str(e)}"}

# New tool for loading a model with GPU acceleration
@mcp.tool()
def load_model(model_path: str) -> dict:
    """Load a model with maximum GPU acceleration without confirmation"""
    import subprocess
    try:
        result = subprocess.run(["lms", "load", model_path, "-y"], capture_output=True, text=True, check=True)
        return {"output": result.stdout.strip()}
    except Exception as e:
        return {"error": f"Failed to load model: {str(e)}"}
    
# New tool for loading a model with GPU acceleration
@mcp.tool()
def unload_model(model_path: str) -> dict:
    """unload a model without confirmation"""
    import subprocess
    try:
        result = subprocess.run(["lms", "unload", model_path], capture_output=True, text=True, check=True)
        return {"output": result.stdout.strip()}
    except Exception as e:
        return {"error": f"Failed to load model: {str(e)}"}

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

@mcp.prompt()
def echo_prompt(message: str) -> str:
    """Create an echo prompt"""
    return f"Please process this message: {message}"


if __name__ == "__main__":
    mcp.run()
