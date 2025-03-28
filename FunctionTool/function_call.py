import importlib.util
from pathlib import Path
import asyncio
from openai import AsyncOpenAI

# 自动加载工具模块
tools = []
global_functions = {}

tool_dir = Path(__file__).parent / 'tools_package'
for p in tool_dir.glob('*.py'):
    module_name = p.stem
    spec = importlib.util.spec_from_file_location(module_name, p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    # 注册工具到列表
    tools.append(mod.tool)
    
    # 将函数导入全局命名空间
    global_functions[mod.tool['function']['name']] = mod.__dict__[mod.tool['function']['name']]

async def call_function(function_name: str, function_args: dict):
    # 使用预加载的全局函数字典
    func = global_functions.get(function_name)
    
    if not callable(func):
        return f"错误：未找到函数 '{function_name}'"
    
    try:
        if asyncio.iscoroutinefunction(func):
            return await func(**function_args)
        else:
            return func(**function_args)
    except TypeError as e:
        return f"参数错误：{str(e)}"

async def main():
    client = AsyncOpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
    response = await client.chat.completions.create(
        model="qwq-32b@8bit",
        messages=[{"role": "user", "content": "Can you say hello to Bob the Builder，compute 5 + 3 and summarize the webpage 'https://baijiahao.baidu.com/s?id=1827850243996290325&wfr=spider&for=pc'?"}],
        tools=tools
    )
    
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        args_dict = eval(tool_call.function.arguments)
        
        result = await call_function(function_name, args_dict)  
        
        if isinstance(result, str) and "错误" in result:
            print(f"⚠️ 调用失败: {function_name} → {result}")
        else:
            print(f"✅ 调用成功: {function_name}({args_dict}) → {result}")

asyncio.run(main())