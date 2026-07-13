from backend.engines.decision_engine.ai_decision_engine import AIDecisionEngine


class DecisionEngineAgent:
    def __init__(self):
        self.name = "Decision Engine Agent"
        self.engine = AIDecisionEngine()

    def handle_request(self, request: dict):
        optimization_plan = request.get("optimization_plan", {})
        return self.engine.evaluate(optimization_plan)
