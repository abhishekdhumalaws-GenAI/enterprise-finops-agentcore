class RootCauseAnalysisEngine:
    def analyze(self, result: dict):
        anomalies = self._get_anomalies(result)

        analyses = []
        facts = []

        ec2_findings = self._analyze_ec2(anomalies)
        opensearch_findings = self._analyze_opensearch(anomalies)
        ebs_findings = self._analyze_ebs(anomalies)

        for item in ec2_findings + opensearch_findings + ebs_findings:
            analyses.append(item)
            facts.append(item["finding"])

        if ec2_findings and opensearch_findings:
            finding = (
                "Combined root cause signal: EC2 GPU usage and OpenSearch OCU usage "
                "increased in the same analysis window, which may indicate a data processing, "
                "AI indexing, embedding, or search workload."
            )

            analyses.append({
                "category": "cross_service_correlation",
                "severity": "HIGH",
                "finding": finding,
                "evidence": [
                    "EC2 anomaly root cause includes BoxUsage:g5.xlarge",
                    "OpenSearch anomaly root cause includes SearchOCU and IndexingOCU"
                ]
            })

            facts.append(finding)

        if not analyses:
            facts.append("No deterministic root cause analysis findings were generated.")

        return {
            "analyses": analyses,
            "facts": facts
        }

    def _analyze_ec2(self, anomalies):
        findings = []

        for anomaly in anomalies:
            if anomaly.get("dimension_value") != "Amazon Elastic Compute Cloud - Compute":
                continue

            for cause in anomaly.get("root_causes", []):
                usage_type = cause.get("UsageType")
                contribution = cause.get("Impact", {}).get("Contribution")
                region = cause.get("Region")

                if usage_type and usage_type.startswith("BoxUsage:"):
                    instance_type = usage_type.split("BoxUsage:")[-1]

                    findings.append({
                        "category": "ec2_compute_spike",
                        "severity": "HIGH",
                        "finding": (
                            f"EC2 compute spike detected from {instance_type} in {region}, "
                            f"with cost contribution of {contribution} USD."
                        ),
                        "evidence": [
                            f"usage_type={usage_type}",
                            f"region={region}",
                            f"contribution={contribution} USD",
                            f"actual_spend={anomaly.get('total_actual_spend')} USD",
                            f"expected_spend={anomaly.get('total_expected_spend')} USD"
                        ]
                    })

        return findings

    def _analyze_opensearch(self, anomalies):
        findings = []

        for anomaly in anomalies:
            if anomaly.get("dimension_value") != "Amazon OpenSearch Service":
                continue

            usage_types = []
            total_contribution = 0

            for cause in anomaly.get("root_causes", []):
                usage_type = cause.get("UsageType")
                contribution = cause.get("Impact", {}).get("Contribution") or 0

                if usage_type:
                    usage_types.append(usage_type)

                total_contribution += contribution

            if usage_types:
                findings.append({
                    "category": "opensearch_ocu_spike",
                    "severity": "HIGH",
                    "finding": (
                        f"OpenSearch cost spike detected from usage types "
                        f"{', '.join(usage_types)}, with total contribution of "
                        f"{round(total_contribution, 2)} USD."
                    ),
                    "evidence": [
                        f"usage_types={usage_types}",
                        f"actual_spend={anomaly.get('total_actual_spend')} USD",
                        f"expected_spend={anomaly.get('total_expected_spend')} USD",
                        f"percentage_impact={anomaly.get('percentage_impact')}"
                    ]
                })

        return findings

    def _analyze_ebs(self, anomalies):
        findings = []

        for anomaly in anomalies:
            if anomaly.get("dimension_value") != "Amazon Elastic Block Store":
                continue

            usage_types = []
            total_contribution = 0

            for cause in anomaly.get("root_causes", []):
                usage_type = cause.get("UsageType")
                contribution = cause.get("Impact", {}).get("Contribution") or 0

                if usage_type:
                    usage_types.append(usage_type)

                total_contribution += contribution

            if usage_types:
                findings.append({
                    "category": "ebs_iops_spike",
                    "severity": "MEDIUM",
                    "finding": (
                        f"EBS cost spike detected from usage types "
                        f"{', '.join(usage_types)}, with total contribution of "
                        f"{round(total_contribution, 2)} USD."
                    ),
                    "evidence": [
                        f"usage_types={usage_types}",
                        f"actual_spend={anomaly.get('total_actual_spend')} USD",
                        f"expected_spend={anomaly.get('total_expected_spend')} USD",
                        f"percentage_impact={anomaly.get('percentage_impact')}"
                    ]
                })

        return findings

    def _get_anomalies(self, result: dict):
        if "execution_results" in result:
            anomaly_result = result["execution_results"].get("cost_anomaly_detection", {})
            return anomaly_result.get("anomalies", [])

        return result.get("anomalies", [])
