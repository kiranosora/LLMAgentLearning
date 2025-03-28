def add(a: int, b: int) -> int:
    return a + b

tool = {
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
}
