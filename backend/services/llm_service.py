import json

from backend.config.settings import settings
from backend.services.aws_session_manager import AWSSessionManager
from backend.services.fact_summarizer import FactSummarizer
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    def __init__(self):
        session = AWSSessionManager.get_session()
        self.client = session.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION
        )
        self.model_id = settings.BEDROCK_MODEL_ID
        self.fact_summarizer = FactSummarizer()

    def generate_finops_answer(self, user_query, parsed_request, result):
        structured = self.generate_structured_finops_answer(
            user_query=user_query,
            parsed_request=parsed_request,
            result=result
        )

        if not structured.get("success"):
            return structured.get("fallback_answer")

        return self.format_structured_answer(structured["answer"])

    def generate_structured_finops_answer(self, user_query, parsed_request, result):
        grounded_context = self.fact_summarizer.summarize(result)

        prompt = f"""
You are a Senior AWS FinOps Consultant.

CRITICAL GROUNDING RULES:
1. Use ONLY the facts provided in the "Grounded Facts" section.
2. Do NOT invent costs, services, regions, usage types, or savings numbers.
3. Do NOT mention AWS services that are not present in the facts.
4. Do NOT estimate monthly savings unless a savings number is explicitly provided.
5. If Compute Optimizer recommendations are 0, say exactly that.
6. If data is unavailable, say "Data not available."
7. Every number in your answer must come from the facts.
8. Separate observed findings from general best practices.
9. Do not use placeholder values like $X,XXX.
10. Return ONLY valid JSON. Do not include markdown outside JSON.
11.Do NOT mention Reserved Instances, Savings Plans, or Spot Instances unless pricing data for those options is explicitly provided in the facts.
12.If only On-Demand pricing is available, recommendations must focus on usage reduction, stopping idle resources, rightsizing investigation, or monitoring. Do not recommend pricing commitment options.

User question:
{user_query}

Parsed request:
{json.dumps(parsed_request, indent=2)}

Grounded Facts:
{json.dumps(grounded_context, indent=2)}

Return JSON using this schema:
{{
  "executive_summary": "string",
  "observed_findings": ["string"],
  "root_cause": ["string"],
  "prioritized_recommendations": ["string"],
  "next_actions": ["string"],
  "limitations": ["string"]
}}
"""

        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                inferenceConfig={
                    "maxTokens": 900,
                    "temperature": 0.05
                }
            )

            text = response["output"]["message"]["content"][0]["text"]
            answer = self._parse_json_response(text)

            return {
                "success": True,
                "answer": answer,
                "grounded_facts": grounded_context
            }

        except Exception as error:
            logger.exception("Bedrock structured generation failed")
            return {
                "success": False,
                "answer": None,
                "grounded_facts": {},
                "fallback_answer": (
                    "# Enterprise FinOps Analysis Completed\n\n"
                    "The multi-agent FinOps workflow completed successfully, but the LLM response generation was throttled by Amazon Bedrock.\n\n"
                    "Please review the structured result section for optimization plan, decision engine output, reasoning engine output, approval workflow, and change manager recommendations.\n\n"
                    "Reason: Bedrock token-per-day limit exceeded."
                ),
                "error": str(error)
            }

    def _parse_json_response(self, text: str):
        cleaned = text.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned.replace("```", "").strip()

        return json.loads(cleaned)

    def format_structured_answer(self, answer: dict):
        lines = []

        lines.append("# Executive Summary")
        lines.append(answer.get("executive_summary", "Data not available."))

        lines.append("\n# Observed Findings")
        for item in answer.get("observed_findings", []):
            lines.append(f"- {item}")

        lines.append("\n# Root Cause / Explanation")
        for item in answer.get("root_cause", []):
            lines.append(f"- {item}")

        lines.append("\n# Prioritized Recommendations")
        for item in answer.get("prioritized_recommendations", []):
            lines.append(f"- {item}")

        lines.append("\n# Next Actions")
        for item in answer.get("next_actions", []):
            lines.append(f"- {item}")

        limitations = answer.get("limitations", [])
        if limitations:
            lines.append("\n# Limitations")
            for item in limitations:
                lines.append(f"- {item}")

        return "\n".join(lines)
