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

import playwright
@mcp.tool()

async def scrape_web_content_from_url(url): # Wrap in an async function for example
    browser = None # Initialize browser to None for finally block
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(proxy={"server": "http://127.0.0.1:1087"}, headless=False)
            page = await browser.new_page()
            try:
                response = await page.goto(url, timeout=30000, wait_until='domcontentloaded') # Consider 'domcontentloaded' or 'load'
                if response is None:
                    # This case might be rare with goto, usually throws error or returns response
                    raise ValueError(f"page.goto() returned None for url {url}")
                if not response.ok:
                     # Check status code
                     print(f"Warning: Received status code {response.status} for {url}")
                     # Decide if you want to proceed or raise error based on status

                # Wait for body explicitly if needed, though inner_text usually handles this
                # await page.wait_for_selector('body', timeout=5000) # Optional: add a small wait

                content = await page.inner_text("body")
                truncated_content = content[:8192]
                print(f"Successfully got content for {url}")
                # Close browser here in the success path of the inner try
                await browser.close()
                browser = None # Set browser to None after successful close
                return content

            except Exception as page_error:
                 print(f"Error during page interaction for {url}: {page_error}")
                 return f"Error processing {url}: {traceback.format_exc()}, {type(page_error)}"

    # Catch broader exceptions like launch failure
    except Exception as e:
        print(f"General Error processing {url}: {e}")
        return f"Error processing {url}: {traceback.format_exc()}, {type(e)}"
    finally:
        # Ensure browser is closed even if errors occurred before explicit close
        if browser:
            print("Closing browser in finally block...")
            await browser.close()
    
@mcp.tool()
def get_memory():
    """
    Return available memory on this machine.
    """
    import psutil
    lms = 0
    mem = psutil.virtual_memory()
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_percent']):
        if 'LM Studio Helper' in proc.info['name'] :
            lms += proc.info['memory_info'].rss
    print({"total_memory":f"{round(mem.total/1024/1024)}MB","free_memory":f"{round(mem.free/1024/1024)}MB"})
    return json.dumps({"total_memory":f"{round(mem.total/1024/1024/1024)}GB","free_memory":f"{round(mem.free/1024/1024/1024)}GB","wired_memory":f"{round(mem.wired/1024/1024/1024)}GB","memory used by lm studio":f"{round(lms/1024/1024/1024)}GB"})

import datetime
@mcp.tool()
def get_current_local_time():
    """
    Returns the current time in local timezone in ISO format.
    """
    return {"local_time": datetime.datetime.now().isoformat()}

@mcp.tool()
def list_inference_model() -> dict:
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
        return json.dumps({"output": obj})
        #return "models"
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
        ret = result.stdout.strip()
        if len(ret) == 0:
            ret = f"unload model {model_path} succeed"
        return {"output": ret}
    except Exception as e:
        return {"error": f"Failed to load model: {str(e)}"}
    
# New tool for downloading a model
@mcp.tool()
def download_model(model_path: str) -> dict:
    """download a model with model_path"""
    import subprocess
    try:
        result = subprocess.run(["lms", "get", model_path, "-y"], capture_output=True, text=True, check=True)
        ret = result.stdout.strip()
        if len(ret) == 0:
            ret = f"get model {model_path} succeed"
        return {"output": ret}
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
