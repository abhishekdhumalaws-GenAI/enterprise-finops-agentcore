from typing import Any, Callable, Dict, List, Optional


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(
        self,
        name: str,
        handler: Callable[..., Any],
        description: str,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        if name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered.")

        self._tools[name] = {
            "name": name,
            "handler": handler,
            "description": description,
            "category": category,
            "metadata": metadata or {},
        }

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "category": tool["category"],
                "metadata": tool["metadata"],
            }
            for tool in self._tools.values()
        ]

    def invoke_tool(
        self,
        name: str,
        **kwargs,
    ) -> Dict[str, Any]:
        tool = self.get_tool(name)

        if not tool:
            return {
                "status": "failed",
                "tool_name": name,
                "error": f"Tool '{name}' is not registered.",
            }

        try:
            result = tool["handler"](**kwargs)

            return {
                "status": "succeeded",
                "tool_name": name,
                "result": result,
            }

        except Exception as error:
            return {
                "status": "failed",
                "tool_name": name,
                "error": str(error),
            }
