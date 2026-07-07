from datetime import datetime, timezone
from typing import Any, Dict


class AgentRuntime:
    def __init__(self):
        self.agents = {}

    def register_agent(self, name: str, agent: Any):
        self.agents[name] = agent

    def list_agents(self):
        return sorted(self.agents.keys())

    def invoke_agent(
        self,
        agent_name: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:

        if agent_name not in self.agents:
            return {
                "status": "error",
                "agent_name": agent_name,
                "message": "Agent is not registered in runtime."
            }

        agent = self.agents[agent_name]

        if hasattr(agent, "handle_request"):
            result = agent.handle_request(payload)
        elif hasattr(agent, "handle"):
            result = agent.handle(payload)
        else:
            return {
                "status": "error",
                "agent_name": agent_name,
                "message": "Agent does not expose handle or handle_request."
            }

        return {
            "status": "success",
            "agent_name": agent_name,
            "invoked_at": datetime.now(timezone.utc).isoformat(),
            "result": result
        }

