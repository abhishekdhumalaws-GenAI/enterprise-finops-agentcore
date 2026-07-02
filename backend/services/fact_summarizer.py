from backend.services.knowledge_graph import FinOpsKnowledgeGraph


class FactSummarizer:
    def __init__(self):
        self.knowledge_graph = FinOpsKnowledgeGraph()

    def summarize(self, result: dict):
        graph = self.knowledge_graph.build(result)

        facts = graph.get("facts", [])

        return {
            "facts": facts,
            "knowledge_graph": {
                "entity_count": len(graph.get("entities", [])),
                "relationship_count": len(graph.get("relationships", [])),
                "entities": graph.get("entities", [])[:20],
                "relationships": graph.get("relationships", [])[:20]
            }
        }
