import boto3
from datetime import date, timedelta


class CostExplorerAgent:
    def __init__(self):
        self.client = boto3.client("ce", region_name="us-east-1")

    def get_last_7_days_cost(self, service_filter=None):
        end_date = date.today()
        start_date = end_date - timedelta(days=7)

        request = {
            "TimePeriod": {
                "Start": start_date.isoformat(),
                "End": end_date.isoformat()
            },
            "Granularity": "DAILY",
            "Metrics": ["UnblendedCost"],
            "GroupBy": [
                {
                    "Type": "DIMENSION",
                    "Key": "SERVICE"
                }
            ]
        }

        response = self.client.get_cost_and_usage(**request)

        results = []

        for day in response["ResultsByTime"]:
            usage_date = day["TimePeriod"]["Start"]

            for group in day.get("Groups", []):
                service_name = group["Keys"][0]
                amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
                unit = group["Metrics"]["UnblendedCost"]["Unit"]

                if service_filter:
                    if service_filter.lower() not in service_name.lower():
                        continue

                results.append({
                    "date": usage_date,
                    "service": service_name,
                    "amount": round(amount, 4),
                    "unit": unit
                })

        return results
