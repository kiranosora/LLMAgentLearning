def say_hello(name: str) -> str:
    print(f"Hello, {name}!")

tool = {
    "type": "function",
    "function": {
        "name": "say_hello",
        "description": "向指定对象问好",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "目标对象的姓名"}
            },
            "required": ["name"]
        }
    }
}
