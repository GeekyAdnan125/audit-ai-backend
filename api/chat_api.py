
from fastapi import APIRouter
from chat.audit_chat_agent import AuditChatAgent

router = APIRouter()
agent = AuditChatAgent()

@router.post("/")
def chat(question: str):
    response = agent.ask(question, "No context yet")
    return {"response": response}
