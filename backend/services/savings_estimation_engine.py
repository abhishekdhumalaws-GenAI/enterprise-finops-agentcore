class SavingsEstimationEngine:
    HOURS_PER_MONTH = 730

    def estimate(self, result: dict):
        savings_context = {
            "estimates": [],
            "facts": []
        }

        pricing = self._get_pricing(result)
        anomalies = self._get_anomalies(result)
        compute = self._get_compute(result)

        if pricing:
            data = pricing.get("data", {})
            instance_type = data.get("instance_type")
            price_per_hour = data.get("price_per_hour_usd")
            region = data.get("region")

            if instance_type and price_per_hour:
                monthly_cost = round(price_per_hour * self.HOURS_PER_MONTH, 2)

                savings_context["estimates"].append({
                    "type": "ondemand_monthly_projection",
                    "service": "EC2",
                    "instance_type": instance_type,
                    "region": region,
                    "price_per_hour_usd": price_per_hour,
                    "estimated_monthly_cost_usd": monthly_cost
                })

                savings_context["facts"].append(
                    f"Estimated monthly On-Demand cost for {instance_type} is {monthly_cost} USD based on {price_per_hour} USD/hour and 730 hours/month."
                )

        ec2_anomaly_impact = 0

        for anomaly in anomalies:
            service = anomaly.get("dimension_value")
            if service == "Amazon Elastic Compute Cloud - Compute":
                impact = anomaly.get("total_impact") or 0
                ec2_anomaly_impact += impact

        if ec2_anomaly_impact:
            ec2_anomaly_impact = round(ec2_anomaly_impact, 2)

            savings_context["estimates"].append({
                "type": "ec2_anomaly_impact",
                "service": "EC2",
                "anomaly_impact_usd": ec2_anomaly_impact
            })

            savings_context["facts"].append(
                f"Total EC2 anomaly impact in the analyzed period is {ec2_anomaly_impact} USD."
            )

        recommendations = compute.get("recommendations", []) if compute else []

        if isinstance(recommendations, list):
            savings_context["facts"].append(
                f"Compute Optimizer recommendations found: {len(recommendations)}."
            )

        return savings_context

    def _get_pricing(self, result: dict):
        if "pricing" in result:
            pricing_wrapper = result.get("pricing", {})

            if pricing_wrapper.get("success"):
                return pricing_wrapper

            pricing_response = pricing_wrapper.get("pricing", {})
            if pricing_response.get("success"):
                return pricing_response

        if "execution_results" in result:
            pricing_result = result["execution_results"].get("pricing", {})

            if pricing_result.get("success"):
                return pricing_result

            pricing_response = pricing_result.get("pricing", {})
            if pricing_response.get("success"):
                return pricing_response

        return None

    def _get_anomalies(self, result: dict):
        if "anomalies" in result:
            return result.get("anomalies", [])

        if "execution_results" in result:
            anomaly_result = result["execution_results"].get("cost_anomaly_detection", {})
            return anomaly_result.get("anomalies", [])

        return []

    def _get_compute(self, result: dict):
        if "compute_optimization" in result:
            return result.get("compute_optimization")

        if "execution_results" in result:
            return result["execution_results"].get("compute_optimization", {})

        return {}
