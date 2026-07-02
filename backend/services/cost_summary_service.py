from collections import defaultdict


class CostSummaryService:
    def summarize(self, cost_data, days=7, service=None):
        total_cost = 0
        service_totals = defaultdict(float)
        daily_totals = defaultdict(float)

        for item in cost_data:
            amount = item["amount"]
            service_name = item["service"]
            usage_date = item["date"]

            total_cost += amount
            service_totals[service_name] += amount
            daily_totals[usage_date] += amount

        top_services = sorted(
            service_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            "total_cost": round(total_cost, 4),
            "currency": "USD",
            "top_services": [
                {"service": name, "amount": round(amount, 4)}
                for name, amount in top_services[:5]
            ],
            "daily_totals": [
                {"date": day, "amount": round(amount, 4)}
                for day, amount in sorted(daily_totals.items())
            ],
            "recommendation": self._generate_recommendation(
                total_cost,
                top_services,
                days,
                service
            )
        }

    def _generate_recommendation(self, total_cost, top_services, days, service):
        service_text = service or "AWS"

        if total_cost == 0:
            return f"No significant {service_text} spend detected in the last {days} days."

        top_service = top_services[0][0] if top_services else service_text

        return (
            f"Highest spend is from {top_service} in the last {days} days. "
            "Review idle resources, usage trends, storage, data transfer, and pricing model."
        )
