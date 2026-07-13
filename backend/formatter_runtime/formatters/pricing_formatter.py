from typing import Any, Dict


def format_pricing_response(result: Dict[str, Any]) -> str:
    pricing = result.get("pricing", {})
    pricing_data = pricing.get("data", {}) if isinstance(pricing, dict) else {}

    if not pricing_data:
        error = (
            pricing.get("error")
            if isinstance(pricing, dict)
            else "Pricing data is unavailable."
        )

        return (
            "# AWS Pricing Lookup\n\n"
            "Pricing information could not be retrieved.\n\n"
            f"Reason: {error or 'Unknown pricing error'}"
        )

    service = pricing_data.get(
        "service",
        result.get("service", "AWS Service"),
    )
    region = pricing_data.get("region", "Unknown region")
    instance_type = pricing_data.get("instance_type", "Unknown instance type")
    price_found = pricing_data.get("price_found", False)
    hourly_price = pricing_data.get("price_per_hour_usd")
    unit = pricing_data.get("unit", "Hrs")
    description = pricing_data.get("description")
    attributes = pricing_data.get("attributes", {})

    if not price_found or hourly_price is None:
        return (
            "# AWS Pricing Lookup\n\n"
            f"No On-Demand price was found for **{instance_type}** "
            f"in **{region}**."
        )

    estimated_daily = round(float(hourly_price) * 24, 2)
    estimated_monthly = round(float(hourly_price) * 24 * 30, 2)

    lines = [
        "# AWS EC2 Pricing",
        "",
        f"**Service:** {service}",
        f"**Region:** {region}",
        f"**Instance Type:** {instance_type}",
        f"**On-Demand Price:** ${float(hourly_price):,.4f} per hour",
        f"**Estimated Daily Cost:** ${estimated_daily:,.2f}",
        f"**Estimated Monthly Cost:** ${estimated_monthly:,.2f}",
        f"**Billing Unit:** {unit}",
    ]

    if description:
        lines.extend([
            "",
            f"**Description:** {description}",
        ])

    if attributes:
        lines.extend([
            "",
            "## Instance Specifications",
        ])

        attribute_labels = {
            "vcpu": "vCPU",
            "memory": "Memory",
            "network_performance": "Network Performance",
            "processor": "Processor",
        }

        for key, value in attributes.items():
            label = attribute_labels.get(
                key,
                key.replace("_", " ").title(),
            )
            lines.append(f"- **{label}:** {value}")

    tool_runtime = result.get("tool_runtime", {})

    if tool_runtime:
        lines.extend([
            "",
            "## Tool Runtime",
            f"- **Selected Tool:** {tool_runtime.get('selected_tool', 'pricing')}",
            f"- **Status:** {tool_runtime.get('status', 'unknown')}",
            f"- **Selection Reason:** {tool_runtime.get('selection_reason', 'N/A')}",
        ])

    return "\n".join(lines)
