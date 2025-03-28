def subtract(a: int, b: int) -> int:
    return a - b

tool = {
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
