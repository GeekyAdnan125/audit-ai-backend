
import pandas as pd

class ReportGenerator:

    def generate_exception_report(self, findings):

        df = pd.DataFrame(findings)

        return df
