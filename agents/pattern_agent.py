
from agents.base_agent import BaseAgent

class PatternAgent(BaseAgent):

    def process(self, df):

        if "vendor" not in df.columns or "amount" not in df.columns:
            return {}

        vendor_spend = df.groupby("vendor")["amount"].sum()

        return vendor_spend

    def generate_findings(self, vendor_spend):

        findings = []

        if len(vendor_spend) == 0:
            return findings

        total = vendor_spend.sum()

        for vendor, amount in vendor_spend.items():

            percent = amount / total * 100

            if percent > 40:

                findings.append({
                    "type": "vendor_concentration",
                    "vendor": vendor,
                    "percent": float(percent)
                })

        return findings
