
class QueryParser:

    def parse(self, question):

        question = question.lower()

        if "duplicate" in question:
            return "duplicate_invoice"

        if "vendor" in question:
            return "vendor_concentration"

        return "general_query"
