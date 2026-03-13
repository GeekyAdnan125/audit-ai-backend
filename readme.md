# AI Audit Backend

Backend service for an AI-powered audit analytics system.
The system analyzes financial datasets such as **Purchase Ledger, Sales Ledger, General Ledger, Vendor Master, and Customer Master** to detect anomalies and audit risks.

---

# Installation

Clone the repository

git clone https://github.com/GeekyAdnan125/audit-ai-backend.git

Go to project folder

cd audit-ai-backend

Create virtual environment

python -m venv venv

Activate virtual environment

Windows

venv\Scripts\activate

Mac / Linux

source venv/bin/activate

Install dependencies

pip install -r requirements.txt

---

# Run the Backend

Start the FastAPI server

uvicorn main:app --reload

Open API documentation in browser

http://127.0.0.1:8000/docs

You can use this page to test APIs such as **file upload and audit analysis**.

---

# Project Structure

audit_ai_backend
│
├── agents/          # AI agents for anomaly detection and audit analysis
├── api/             # API endpoints
├── chat/            # Chat assistant logic
├── config/          # Configuration settings
├── ingestion/       # File loading and schema mapping
├── llm/             # LLM integration
├── orchestrator/    # Agent pipeline controller
├── processing/      # Data normalization and preprocessing
├── reporting/       # Report generation
├── rules/           # Audit rules and rule engine
├── storage/         # Database and findings storage
├── utils/           # Utility functions

├── main.py          # FastAPI application entry point
├── requirements.txt # Python dependencies
└── README.md        # Project documentation
