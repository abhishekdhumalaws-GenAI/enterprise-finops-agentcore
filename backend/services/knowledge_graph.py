from backend.services.savings_estimation_engine import SavingsEstimationEngine
from backend.services.optimization_recommendation_engine import OptimizationRecommendationEngine
from backend.services.root_cause_analysis_engine import RootCauseAnalysisEngine

class FinOpsKnowledgeGraph:
    def build(self, result: dict):
        self.savings_estimation_engine = SavingsEstimationEngine()
        self.optimization_recommendation_engine = OptimizationRecommendationEngine()
        self.root_cause_analysis_engine = RootCauseAnalysisEngine()

        graph = {
            "entities": [],
            "relationships": [],
            "facts": []
        }

        self._add_root_cause_analysis(result, graph)
        self._add_organizations_entities(result, graph)
        self._add_optimization_recommendations(result, graph)
        self._add_cost_entities(result, graph)
        self._add_anomaly_entities(result, graph)
        self._add_compute_entities(result, graph)
        self._add_pricing_entities(result, graph)
        self._add_budget_entities(result, graph)
        self._add_savings_entities(result, graph)

        return graph

    def _add_entity(self, graph, entity_type, name, properties=None):
        if not name:
            name = "unknown"

        entity = {
            "type": entity_type,
            "name": name,
            "properties": properties or {}
        }

        if entity not in graph["entities"]:
            graph["entities"].append(entity)

    def _add_relationship(self, graph, source, relation, target, properties=None):
        graph["relationships"].append({
            "source": source or "unknown",
            "relation": relation,
            "target": target or "unknown",
            "properties": properties or {}
        })

    def _add_fact(self, graph, fact):
        if fact:
            graph["facts"].append(fact)

    def _add_cost_entities(self, result, graph):
        cost_source = None

        if "cost_summary" in result:
            cost_source = result
        elif "cost_analysis" in result:
            cost_source = result.get("cost_analysis")
        elif "execution_results" in result:
            cost_source = result["execution_results"].get("cost_analysis")

        if not cost_source:
            return

        summary = cost_source.get("cost_summary")
        if not summary:
            return

        currency = summary.get("currency", "USD")
        total_cost = summary.get("total_cost")

        self._add_entity(
            graph,
            "cost_summary",
            "total_cost",
            {
                "amount": total_cost,
                "currency": currency
            }
        )

        self._add_fact(graph, f"Total cost is {total_cost} {currency}")

        for service in summary.get("top_services", []):
            service_name = service.get("service")
            amount = service.get("amount")

            self._add_entity(
                graph,
                "aws_service",
                service_name,
                {
                    "cost": amount,
                    "currency": currency
                }
            )

            self._add_relationship(
                graph,
                service_name,
                "contributes_to",
                "total_cost",
                {
                    "amount": amount,
                    "currency": currency
                }
            )

            self._add_fact(
                graph,
                f"{service_name} cost is {amount} {currency}"
            )

        daily_totals = summary.get("daily_totals", [])
        if daily_totals:
            highest_day = max(
                daily_totals,
                key=lambda item: item.get("amount", 0)
            )

            self._add_entity(
                graph,
                "date",
                highest_day.get("date"),
                {
                    "cost": highest_day.get("amount"),
                    "currency": currency
                }
            )

            self._add_relationship(
                graph,
                highest_day.get("date"),
                "has_highest_daily_cost",
                "total_cost",
                {
                    "amount": highest_day.get("amount"),
                    "currency": currency
                }
            )

            self._add_fact(
                graph,
                f"Highest daily cost was {highest_day.get('amount')} {currency} on {highest_day.get('date')}"
            )

    def _add_anomaly_entities(self, result, graph):
        anomaly_source = None

        if "anomaly_analysis" in result:
            anomaly_source = result.get("anomaly_analysis")
        elif "execution_results" in result:
            anomaly_source = result["execution_results"].get("cost_anomaly_detection")
        elif "anomalies" in result:
            anomaly_source = result

        if not anomaly_source:
            return

        anomalies = anomaly_source.get("anomalies", [])

        self._add_fact(graph, f"Anomalies found: {len(anomalies)}")

        sorted_anomalies = sorted(
            anomalies,
            key=lambda item: item.get("total_impact") or 0,
            reverse=True
        )

        for anomaly in sorted_anomalies[:5]:
            anomaly_id = anomaly.get("anomaly_id")
            service = anomaly.get("dimension_value")
            start_date = anomaly.get("start_date")
            end_date = anomaly.get("end_date")
            actual = anomaly.get("total_actual_spend")
            expected = anomaly.get("total_expected_spend")
            impact = anomaly.get("total_impact")
            percentage = anomaly.get("percentage_impact")

            self._add_entity(
                graph,
                "anomaly",
                anomaly_id,
                {
                    "service": service,
                    "start_date": start_date,
                    "end_date": end_date,
                    "actual_spend": actual,
                    "expected_spend": expected,
                    "impact": impact,
                    "percentage_impact": percentage
                }
            )

            self._add_relationship(
                graph,
                service,
                "has_anomaly",
                anomaly_id,
                {
                    "impact": impact,
                    "actual_spend": actual,
                    "expected_spend": expected
                }
            )

            self._add_fact(
                graph,
                f"Anomaly for {service}: actual={actual} USD, expected={expected} USD, impact={impact} USD, percentage={percentage}, start={start_date}, end={end_date}"
            )

            for cause in anomaly.get("root_causes", []):
                cause_service = cause.get("Service")
                region = cause.get("Region")
                usage_type = cause.get("UsageType")
                contribution = cause.get("Impact", {}).get("Contribution")

                if usage_type:
                    self._add_entity(
                        graph,
                        "usage_type",
                        usage_type,
                        {
                            "service": cause_service,
                            "region": region,
                            "contribution": contribution
                        }
                    )

                    self._add_relationship(
                        graph,
                        usage_type,
                        "caused_anomaly",
                        anomaly_id,
                        {
                            "contribution": contribution,
                            "region": region
                        }
                    )

                self._add_fact(
                    graph,
                    f"Root cause: service={cause_service}, region={region}, usage_type={usage_type}, contribution={contribution} USD"
                )

    def _add_compute_entities(self, result, graph):
        compute_source = None

        if "compute_optimization" in result:
            compute_source = result.get("compute_optimization")
        elif "execution_results" in result:
            compute_source = result["execution_results"].get("compute_optimization")

        if not compute_source:
            return

        recommendations = compute_source.get("recommendations", [])

        if isinstance(recommendations, list):
            self._add_fact(
                graph,
                f"Compute Optimizer recommendations found: {len(recommendations)}"
            )

            for rec in recommendations[:5]:
                instance_arn = rec.get("instance_arn")
                finding = rec.get("finding")

                self._add_entity(
                    graph,
                    "compute_recommendation",
                    instance_arn or "unknown_instance",
                    {
                        "finding": finding,
                        "recommendation": rec
                    }
                )
        else:
            self._add_fact(
                graph,
                "Compute Optimizer recommendations unavailable."
            )

    def _add_pricing_entities(self, result, graph):
        pricing_source = None

        if "pricing" in result:
            pricing_source = result.get("pricing")
        elif "execution_results" in result:
            pricing_source = result["execution_results"].get("pricing")

        if not pricing_source:
            return

        pricing = pricing_source.get("pricing", {})

        if not pricing.get("success"):
            self._add_fact(graph, "Pricing data unavailable.")
            return

        data = pricing.get("data", {})

        instance_type = data.get("instance_type")
        region = data.get("region")
        price_per_hour = data.get("price_per_hour_usd")

        self._add_entity(
            graph,
            "pricing",
            instance_type,
            {
                "service": data.get("service"),
                "region": region,
                "price_per_hour_usd": price_per_hour,
                "unit": data.get("unit"),
                "operating_system": data.get("operating_system"),
                "tenancy": data.get("tenancy")
            }
        )

        self._add_relationship(
            graph,
            instance_type,
            "has_on_demand_price",
            region,
            {
                "price_per_hour_usd": price_per_hour,
                "unit": data.get("unit")
            }
        )

        self._add_fact(
            graph,
            f"EC2 instance {instance_type} costs {price_per_hour} USD per hour in {region}"
        )

        if price_per_hour:
            monthly_cost = round(price_per_hour * 730, 2)
            self._add_fact(
                graph,
                f"Estimated monthly On-Demand cost for {instance_type} is {monthly_cost} USD based on {price_per_hour} USD/hour and 730 hours/month."
        )

    def _add_budget_entities(self, result, graph):
        budget_source = None

        if "budgets" in result:
            budget_source = result.get("budgets")
        elif "execution_results" in result:
            budget_source = result["execution_results"].get("budgets")

        if not budget_source:
            return

        budgets = budget_source.get("budgets", {})

        if not budgets.get("success"):
            self._add_fact(graph, "AWS Budgets data unavailable.")
            return

        data = budgets.get("data", {})
        budget_items = data.get("budgets", [])

        self._add_fact(
            graph,
            f"AWS Budgets found: {data.get('budgets_found', 0)}"
        )

        for item in budget_items[:5]:
            name = item.get("budget_name")
            limit_amount = item.get("limit_amount")
            actual_spend = item.get("actual_spend")
            forecasted_spend = item.get("forecasted_spend")
            unit = item.get("limit_unit")

            self._add_entity(
                graph,
                "budget",
                name,
                {
                    "limit_amount": limit_amount,
                    "actual_spend": actual_spend,
                    "forecasted_spend": forecasted_spend,
                    "unit": unit
                }
            )

            self._add_fact(
                graph,
                f"Budget {name}: limit={limit_amount} {unit}, actual={actual_spend} {unit}, forecasted={forecasted_spend} {unit}"
            )

    def _add_savings_entities(self, result, graph):
        savings = self.savings_estimation_engine.estimate(result)

        for fact in savings.get("facts", []):
            self._add_fact(graph, fact)

        for estimate in savings.get("estimates", []):
            estimate_type = estimate.get("type")

            self._add_entity(
                graph,
                "savings_estimate",
                estimate_type,
                estimate
            )

    def _add_optimization_recommendations(self, result, graph):
        optimization = self.optimization_recommendation_engine.generate(result)

        for fact in optimization.get("facts", []):
            self._add_fact(graph, fact)

        for rec in optimization.get("recommendations", []):
            self._add_entity(
                graph,
                "optimization_recommendation",
                rec.get("category"),
                rec
            )

    def _add_organizations_entities(self, result, graph):
        org_source = None

        if "organizations" in result:
            org_source = result.get("organizations")
        elif "execution_results" in result:
            org_source = result["execution_results"].get("organizations")

        if not org_source:
            return

        organizations = org_source.get("organizations", {})

        if not organizations.get("success"):
            self._add_fact(graph, "AWS Organizations data unavailable.")
            return

        data = organizations.get("data", {})
        accounts = data.get("accounts", [])

        self._add_fact(
            graph,
            f"AWS Organizations accounts found: {data.get('accounts_found', 0)}"
        )

        for account in accounts[:10]:
            account_id = account.get("account_id")
            name = account.get("name")
            status = account.get("status")
            joined_method = account.get("joined_method")

            self._add_entity(
                graph,
                "aws_account",
                account_id,
                {
                    "name": name,
                    "status": status,
                    "joined_method": joined_method
                }
            )

            self._add_fact(
                graph,
                f"AWS account {account_id} named {name} has status {status} and joined method {joined_method}."
            )

    def _add_root_cause_analysis(self, result, graph):
        root_cause = self.root_cause_analysis_engine.analyze(result)

        for fact in root_cause.get("facts", []):
            self._add_fact(graph, fact)

        for analysis in root_cause.get("analyses", []):
            self._add_entity(
                graph,
                "root_cause_analysis",
                analysis.get("category"),
                analysis
            )
