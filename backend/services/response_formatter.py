class ResponseFormatter:
    def format(self, result):
        summary = result["cost_summary"]
        service = result["service"]
        days = result["days"]
        recommendations = result["recommendations"]

        lines = []

        lines.append(f"FinOps Analysis for {service}")
        lines.append(f"Period: Last {days} days")
        lines.append(f"Total Cost: {summary['total_cost']} {summary['currency']}")

        if summary["top_services"]:
            lines.append("Top Services:")
            for item in summary["top_services"]:
                lines.append(f"- {item['service']}: {item['amount']} {summary['currency']}")
        else:
            lines.append("No billable service usage found for this period.")

        lines.append("Recommendations:")
        for rec in recommendations:
            lines.append(f"- {rec}")

        return "\n".join(lines)
