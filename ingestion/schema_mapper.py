
class SchemaMapper:

    def map_schema(self, df):

        mapping = {
            "Invoice Number": "invoice",
            "Vendor Name": "vendor",
            "Amount": "amount",
            "Date": "date"
        }

        df = df.rename(columns=mapping)

        return df
