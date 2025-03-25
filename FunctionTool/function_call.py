from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
def say_hello(name: str) -> str:
    print(f"Hello, {name}!")

# 新增加减函数
def add(a: int, b: int) -> int:
    return a + b

def subtract(a: int, b: int) -> int:
    return a - b

# 自动调用函数的通用方法
def call_function(function_name: str, function_args: dict):
    """
    根据函数名和参数自动调用全局定义的工具函数

    参数:
        function_name (str): 函数名称
        function_args (dict): 关键字参数字典

    返回:
        调用结果或错误信息
    """

    # 通过globals()动态查找函数对象（无需显式维护映射表）
    func = globals().get(function_name)

    if not callable(func):
        return f"错误：未找到函数 '{function_name}' 或无效对象"

    try:
        # 执行函数并返回结果
        return func(**function_args)
    except TypeError as e:
        return f"参数错误：{str(e)}"

# 定义支持的工具集合
tools = [
    {
        "type": "function",
        "function": {
            "name": "say_hello",
            "description": "向指定对象问好",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "目标对象的姓名"
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "执行加法运算",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer", "description": "第一个加数"},
                    "b": {"type": "integer", "description": "第二个加数"}
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "subtract",
            "description": "执行减法运算",
            "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "integer", "description": "被减数"},
                        "b": {"type": "integer", "description": "减数"}
                    },
                    "required": ["a", "b"]
                }
        }
    }
]

# 发送请求并处理响应
response = client.chat.completions.create(
    model="qwq-32b@8bit",
    messages=[{"role": "user", "content": "Can you say hello to Bob the Builder and compute 5 + 3?"}],
    tools=tools
)

# 处理多个可能的工具调用
for tool_call in response.choices[0].message.tool_calls:
    function_name = tool_call.function.name
    args_dict = eval(tool_call.function.arguments)

    # 调用通用函数执行器
    result = call_function(function_name, args_dict)

    if isinstance(result, str) and "错误" in result:
        print(f"⚠️ 调用失败: {function_name} → {result}")
    else:
        print(f"✅ 调用成功: {function_name}({args_dict}) → {result}")
