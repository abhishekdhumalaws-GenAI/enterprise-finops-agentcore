from backend.formatter_runtime.formatter_registry_singleton import (
    formatter_registry,
)
from backend.formatter_runtime.formatters.pricing_formatter import (
    format_pricing_response,
)


def bootstrap_formatters():
    if not formatter_registry.has_formatter("pricing"):
        formatter_registry.register_formatter(
            intent="pricing",
            formatter=format_pricing_response,
        )

    return formatter_registry
