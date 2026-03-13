
from llm.llm_client import LLMClient
from llm.prompts import audit_prompt

class ReasoningEngine:

    def __init__(self):
        self.llm = LLMClient()

    def explain(self, question, context):

        prompt = audit_prompt(question, context)

        return self.llm.ask(prompt)
