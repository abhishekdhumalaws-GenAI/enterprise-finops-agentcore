import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from backend.agent_runtime.execution_context import ExecutionContext

class AgentRuntime:
    def __init__(self):
        self.agents = {}
        self.executions = []

    def register_agent(self, name: str, agent: Any):
        self.agents[name] = agent

    def list_agents(self):
        return sorted(self.agents.keys())

    def list_executions(self, limit: int = 20):
        return self.executions[-limit:]

    def invoke_agent(
        self,
        agent_name: str,
        payload: Optional[Dict[str, Any]] = None,
        context: Optional[ExecutionContext] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:

        if context is None:
            context = ExecutionContext(
                correlation_id=correlation_id,
                payload=payload or {}
            )

        execution_id = f"agent-exec-{uuid.uuid4()}"
        started_at = datetime.now(timezone.utc).isoformat()
        start_time = time.time()

        execution_record = {
            "execution_id": execution_id,
            "correlation_id": correlation_id,
            "agent_name": agent_name,
            "status": "RUNNING",
            "started_at": started_at,
            "completed_at": None,
            "duration_ms": None,
            "context": context.to_dict(),
            "input": context.payload,
            "output": None,
            "error": None
        }

        try:
            if agent_name not in self.agents:
                raise ValueError(
                    f"Agent '{agent_name}' is not registered in runtime."
                )

            agent = self.agents[agent_name]

            if hasattr(agent, "handle_context"):
                result = agent.handle_context(context)
            elif hasattr(agent, "handle_request"):
                result = agent.handle_request(context.payload)
            elif hasattr(agent, "handle"):
                result = agent.handle(context.payload)

            else:
                raise AttributeError(
                    f"Agent '{agent_name}' does not expose."
                    "handle_context, handle or handle_request."
                )

            execution_record["status"] = "SUCCEEDED"
            execution_record["output"] = result
            context.add_result(agent_name, result)
            execution_record["context"] = context.to_dict()

        except Exception as error:
            execution_record["status"] = "FAILED"
            execution_record["error"] = str(error)

        finally:
            completed_at = datetime.now(timezone.utc).isoformat()
            duration_ms = round((time.time() - start_time) * 1000, 2)

            execution_record["completed_at"] = completed_at
            execution_record["duration_ms"] = duration_ms

            self.executions.append(execution_record)

        return execution_record
