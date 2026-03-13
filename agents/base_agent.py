
class BaseAgent:

    def run(self, df):

        processed = self.process(df)
        findings = self.generate_findings(processed)

        return findings

    def process(self, df):
        raise NotImplementedError

    def generate_findings(self, result):
        raise NotImplementedError
