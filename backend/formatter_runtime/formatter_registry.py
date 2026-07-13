from typing import Any, Callable, Dict, Optional


class FormatterRegistry:
    def __init__(self):
        self._formatters: Dict[str, Callable[[Dict[str, Any]], str]] = {}

    def register_formatter(
        self,
        intent: str,
        formatter: Callable[[Dict[str, Any]], str],
    ):
        normalized_intent = intent.strip().lower()

        if normalized_intent in self._formatters:
            raise ValueError(
                f"Formatter for intent '{normalized_intent}' is already registered."
            )

        self._formatters[normalized_intent] = formatter

    def has_formatter(self, intent: str) -> bool:
        return intent.strip().lower() in self._formatters

    def get_formatter(
        self,
        intent: str,
    ) -> Optional[Callable[[Dict[str, Any]], str]]:
        return self._formatters.get(intent.strip().lower())

    def list_formatters(self):
        return sorted(self._formatters.keys())

    def format(
        self,
        intent: str,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        formatter = self.get_formatter(intent)

        if not formatter:
            return {
                "status": "failed",
                "intent": intent,
                "formatted_response": None,
                "error": f"No formatter registered for intent '{intent}'.",
            }

        try:
            formatted_response = formatter(result)

            return {
                "status": "succeeded",
                "intent": intent,
                "formatted_response": formatted_response,
                "error": None,
            }

        except Exception as error:
            return {
                "status": "failed",
                "intent": intent,
                "formatted_response": None,
                "error": str(error),
            }

