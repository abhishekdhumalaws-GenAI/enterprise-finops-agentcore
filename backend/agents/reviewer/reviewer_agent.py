class ReviewerAgent:
    def __init__(self):
        self.name = "FinOps Reviewer Agent"

    def review(self, structured_answer: dict, grounded_facts: dict):
        facts_text = " ".join(grounded_facts.get("facts", []))

        issues = []

        answer_text = str(structured_answer)

        forbidden_placeholders = [
            "$X,XXX",
            "t2.micro",
            "RDS",
            "Reserved Instances",
            "S3 Glacier"
        ]

        for item in forbidden_placeholders:
            if item in answer_text and item not in facts_text:
                issues.append(f"Unsupported item found: {item}")

        if not structured_answer.get("executive_summary"):
            issues.append("Missing executive_summary")

        if not structured_answer.get("observed_findings"):
            issues.append("Missing observed_findings")

        if issues:
            return {
                "approved": False,
                "issues": issues
            }

        return {
            "approved": True,
            "issues": []
        }
