
from agents.base_agent import BaseAgent

class AnomalyAgent(BaseAgent):

    def process(self, df):

        if not all(col in df.columns for col in ["invoice","vendor","amount"]):
            return df.head(0)

        duplicates = df[df.duplicated(
            ["invoice", "vendor", "amount"],
            keep=False
        )]

        return duplicates

    def generate_findings(self, duplicates):

        findings = []

        for _, row in duplicates.iterrows():

            findings.append({
                "type": "duplicate_invoice",
                "invoice": row.get("invoice"),
                "vendor": row.get("vendor"),
                "amount": row.get("amount")
            })

        return findings
