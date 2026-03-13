
import pandas as pd

class DataNormalizer:

    def normalize(self, df):

        df.columns = df.columns.str.lower()

        if "amount" in df.columns:
            df["amount"] = df["amount"].astype(float)

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        return df
