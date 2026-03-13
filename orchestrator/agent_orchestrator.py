
from agents.anomaly_agent import AnomalyAgent
from agents.pattern_agent import PatternAgent

class AgentOrchestrator:

    def __init__(self):

        self.agents = [
            AnomalyAgent(),
            PatternAgent()
        ]

    def run(self, df):

        findings = []

        for agent in self.agents:

            result = agent.run(df)

            findings.extend(result)

        return findings
