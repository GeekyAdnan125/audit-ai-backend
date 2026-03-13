
from llm.reasoning_engine import ReasoningEngine

class AuditChatAgent:

    def __init__(self):
        self.engine = ReasoningEngine()

    def ask(self, question, context):
        return self.engine.explain(question, context)
