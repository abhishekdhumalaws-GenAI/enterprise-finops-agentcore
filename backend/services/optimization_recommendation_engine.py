class OptimizationRecommendationEngine:
    def generate(self, result: dict):
        recommendations = []
        facts = []

        anomalies = self._get_anomalies(result)
        pricing = self._get_pricing(result)
        budgets = self._get_budgets(result)
        cloudwatch = self._get_cloudwatch(result)
        compute = self._get_compute(result)
        ec2_discovery = self._get_ec2_discovery(result)

        ec2_anomaly_impact = self._calculate_ec2_anomaly_impact(anomalies)
        instance_type = self._extract_instance_type(anomalies)

        if ec2_anomaly_impact > 0:
            recommendations.append({
                "priority": "HIGH",
                "category": "EC2 anomaly investigation",
                "recommendation": (
                    f"Investigate EC2 anomalies with total impact of "
                    f"{ec2_anomaly_impact} USD."
                ),
                "reason": "Cost Anomaly Detection identified unexpected EC2 spend.",
                "evidence": f"EC2 anomaly impact = {ec2_anomaly_impact} USD"
            })

            facts.append(
                f"Optimization recommendation: Investigate EC2 anomalies with total impact of {ec2_anomaly_impact} USD."
            )

        if instance_type:
            recommendations.append({
                "priority": "HIGH",
                "category": "Instance usage review",
                "recommendation": (
                    f"Review usage of {instance_type} instances and verify whether "
                    "they are required for the workload."
                ),
                "reason": "The instance type appeared in EC2 anomaly root cause data.",
                "evidence": f"Discovered instance type = {instance_type}"
            })

            facts.append(
                f"Optimization recommendation: Review usage of {instance_type} instances."
            )

        if pricing:
            data = pricing.get("data", {})
            price_per_hour = data.get("price_per_hour_usd")
            priced_instance = data.get("instance_type")
            region = data.get("region")

            if price_per_hour and priced_instance:
                monthly_cost = round(price_per_hour * 730, 2)

                recommendations.append({
                    "priority": "MEDIUM",
                    "category": "On-Demand cost projection",
                    "recommendation": (
                        f"Monitor {priced_instance} usage because continuous "
                        f"On-Demand usage may cost approximately {monthly_cost} USD/month."
                    ),
                    "reason": "AWS Pricing API returned On-Demand hourly pricing.",
                    "evidence": (
                        f"{priced_instance} costs {price_per_hour} USD/hour "
                        f"in {region}; estimated monthly cost = {monthly_cost} USD."
                    )
                })

                facts.append(
                    f"Optimization recommendation: Continuous On-Demand usage of {priced_instance} may cost approximately {monthly_cost} USD/month."
                )

        if compute:
            compute_recs = compute.get("recommendations", [])

            if isinstance(compute_recs, list) and len(compute_recs) == 0:
                recommendations.append({
                    "priority": "LOW",
                    "category": "Compute Optimizer",
                    "recommendation": (
                        "No Compute Optimizer rightsizing recommendations were found. "
                        "Do not claim rightsizing savings until recommendations or utilization data are available."
                    ),
                    "reason": "Compute Optimizer returned zero recommendations.",
                    "evidence": "Compute Optimizer recommendations = 0"
                })

                facts.append(
                    "Optimization recommendation: Compute Optimizer returned zero recommendations."
                )

        if budgets:
            budget_data = budgets.get("data", {})
            budgets_found = budget_data.get("budgets_found", 0)

            if budgets_found == 0:
                recommendations.append({
                    "priority": "MEDIUM",
                    "category": "Cost governance",
                    "recommendation": (
                        "Create an AWS Budget for EC2 and overall monthly AWS spend."
                    ),
                    "reason": "No AWS Budgets were found in the account.",
                    "evidence": "AWS Budgets found = 0"
                })

                facts.append(
                    "Optimization recommendation: Create AWS Budgets because no budgets were found."
                )

        if cloudwatch:
            cw_data = cloudwatch.get("data", {})

            if cw_data.get("metric_found") is False:
                recommendations.append({
                    "priority": "MEDIUM",
                    "category": "Utilization visibility",
                    "recommendation": (
                        "CloudWatch utilization analysis is unavailable because no EC2 instance ID was discovered."
                    ),
                    "reason": "CloudWatch requires a resource identifier such as an EC2 instance ID.",
                    "evidence": cw_data.get("message")
                })

                facts.append(
                    "Optimization recommendation: CloudWatch utilization analysis is unavailable because no EC2 instance ID was discovered."
                )

        if ec2_discovery:
            discovery_data = ec2_discovery.get("data", {})
            instances_found = discovery_data.get("instances_found", 0)

            if instances_found == 0:
                recommendations.append({
                    "priority": "LOW",
                    "category": "Resource discovery",
                    "recommendation": (
                        "No current EC2 instances matched the discovered anomaly instance type. "
                        "The anomalous resource may have been terminated."
                    ),
                    "reason": "EC2 Discovery found zero matching instances.",
                    "evidence": f"instances_found = {instances_found}"
                })

                facts.append(
                    "Optimization recommendation: No current EC2 instances matched the anomaly instance type."
                )

        return {
            "recommendations": recommendations,
            "facts": facts
        }

    def _get_anomalies(self, result: dict):
        if "execution_results" in result:
            anomaly_result = result["execution_results"].get("cost_anomaly_detection", {})
            return anomaly_result.get("anomalies", [])

        return result.get("anomalies", [])

    def _get_pricing(self, result: dict):
        if "execution_results" in result:
            pricing_result = result["execution_results"].get("pricing", {})
            return pricing_result.get("pricing", {})

        return result.get("pricing", {})

    def _get_budgets(self, result: dict):
        if "execution_results" in result:
            budgets_result = result["execution_results"].get("budgets", {})
            return budgets_result.get("budgets", {})

        return result.get("budgets", {})

    def _get_cloudwatch(self, result: dict):
        if "execution_results" in result:
            cloudwatch_result = result["execution_results"].get("cloudwatch", {})
            return cloudwatch_result.get("cloudwatch", {})

        return result.get("cloudwatch", {})

    def _get_compute(self, result: dict):
        if "execution_results" in result:
            return result["execution_results"].get("compute_optimization", {})

        return result.get("compute_optimization", {})

    def _get_ec2_discovery(self, result: dict):
        if "execution_results" in result:
            discovery_result = result["execution_results"].get("ec2_discovery", {})
            return discovery_result.get("ec2_discovery", {})

        return result.get("ec2_discovery", {})

    def _calculate_ec2_anomaly_impact(self, anomalies):
        total = 0

        for anomaly in anomalies:
            if anomaly.get("dimension_value") == "Amazon Elastic Compute Cloud - Compute":
                total += anomaly.get("total_impact") or 0

        return round(total, 2)

    def _extract_instance_type(self, anomalies):
        for anomaly in anomalies:
            for cause in anomaly.get("root_causes", []):
                usage_type = cause.get("UsageType")

                if usage_type and usage_type.startswith("BoxUsage:"):
                    return usage_type.split("BoxUsage:")[-1]

        return None
