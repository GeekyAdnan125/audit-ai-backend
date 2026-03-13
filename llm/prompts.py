
def audit_prompt(question, context):

    return f"""
You are an AI audit assistant.

Context:
{context}

Question:
{question}

Answer clearly for auditors.
"""
