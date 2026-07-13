from backend.tool_runtime.tool_orchestrator_singleton import tool_orchestrator


class PricingAgent:
    def __init__(self):
        self.name = "Pricing Agent"
        self.tool_orchestrator = tool_orchestrator

    def handle(self, request: dict):
        service = request.get("service") or "EC2"
        region = request.get("region") or "US East (N. Virginia)"
        instance_type = request.get("instance_type") or "g5.xlarge"

        orchestration_result = self.tool_orchestrator.orchestrate(
            intent="pricing",
            service=service,
            arguments={
                "service": service,
                "region_name": region,
                "instance_type": instance_type,
            },
        )

        if orchestration_result.get("status") != "succeeded":
            error = orchestration_result.get(
                "error",
                "Pricing tool invocation failed.",
            )

            return {
                "agent": self.name,
                "service": service,
                "success": False,
                "pricing": {
                    "success": False,
                    "data": None,
                    "error": error,
                },
                "tool_runtime": {
                    "selected_tool": orchestration_result.get("selected_tool"),
                    "selection_reason": orchestration_result.get(
                        "selection_reason"
                    ),
                    "status": orchestration_result.get("status"),
                    "error": error,
                },
            }

        pricing_result = orchestration_result.get("tool_result") or {}

        return {
            "agent": self.name,
            "service": service,
            "success": True,
            "pricing": pricing_result,
            "tool_runtime": {
                "selected_tool": orchestration_result.get("selected_tool"),
                "selection_reason": orchestration_result.get(
                    "selection_reason"
                ),
                "status": orchestration_result.get("status"),
                "error": orchestration_result.get("error"),
            },
        }
