# Financial_Document_Analyzer_Debugged
A Multi Agent document analyzer system which extracts financial information from a financial report or statements and provides analysis reports, risk assessment and investment recommendations.

📊 Financial Document Analyzer – Debug Assignment (Completed)
🔍 Project Overview

This project is a multi-agent AI-powered financial document analysis system built using:

FastAPI

CrewAI

LangChain PDF Loader

LLM (migrated from OpenAI to Ollama)

The system is designed to:

Upload financial PDF documents

Verify document type

Extract structured financial metrics

Perform financial analysis

Assess risks

Provide investment insights

🐛 Debugging Summary

The original project was intentionally broken.
Below is a complete breakdown of all major bugs identified and how they were fixed.

🧩 1️⃣ LLM Not Initialized
❌ Original Bug

In agents.py:

llm = llm

No LLM was actually initialized.

🔎 Root Cause

No OpenAI configuration

No API key loading

No proper LLM instantiation

Agents created without a working model

✅ Fix Implemented

Migrated to local Ollama model:

llm = LLM(
    model="ollama/mistral",
    base_url="http://localhost:11434",
    temperature=0.7
)
🚀 Impact

System became operational

No API key required

No rate limits

Faster local inference

🧩 2️⃣ Uploaded File Path Not Passed to Agent
❌ Original Bug

run_crew() ignored uploaded file:

financial_crew.kickoff({'query': query})

File path was never passed.

🔎 Impact

Uploaded file was saved

But system always read data/sample.pdf

User upload was ignored

✅ Fix
financial_crew.kickoff(
    inputs={
        "query": query,
        "path": file_path
    }
)
🚀 Impact

System now analyzes the actual uploaded document.

🧩 3️⃣ PDF Loader Import Missing
❌ Original Bug

Pdf(file_path=path).load() was used without importing Pdf.

🔎 Impact

Application crashed on startup.

✅ Fix

Replaced with:

from langchain_community.document_loaders import PyPDFLoader

And:

loader = PyPDFLoader(path)
docs = loader.load()
🚀 Impact

PDF loading works correctly.

🧩 4️⃣ Entire PDF Sent to LLM (Hallucination Issue)
❌ Original Behavior

Tool returned:

return full_report

Entire document text was passed to LLM.

🔎 Impact

LLM hallucinated:

Fake revenue numbers

Fake EBITDA

Fake risks

Fake ratios

Unreliable output.

✅ Fix

Rebuilt FinancialDocumentTool to:

Extract only target metrics

Normalize units (B → millions)

Use regex-based numeric extraction

Return structured JSON

Example output:

{
  "revenue": 16661.0,
  "net_income": 1200.0,
  "operating_income": 900.0,
  "gross_profit": 2900.0
}
🚀 Impact

No hallucinated numbers

Deterministic extraction

Faster response

Reduced token usage

🧩 5️⃣ Pydantic v2 Validation Errors
❌ Errors Encountered

args_schema overridden by non-annotated attribute

TARGET_METRICS missing annotation

Tool instance validation failure

🔎 Root Cause

Pydantic v2 requires:

Strict type annotations

ClassVar for constants

✅ Fix
from typing import ClassVar, Dict, List, Type
TARGET_METRICS: ClassVar[Dict[str, List[str]]] = {...}
args_schema: Type[BaseModel] = FinancialDocumentInput
🚀 Impact

Fully compatible with Pydantic v2

No validation crashes

Stable agent initialization

🧩 6️⃣ Nonexistent Tool “Calculations” Called
❌ Problem

Agent attempted:

Action: Calculations

But no such tool existed.

🔎 Impact

Infinite loop

“Maximum iterations reached”

Timeout errors

✅ Fix

Moved all margin calculations into tool:

operating_margin = (operating_income / revenue) * 100

Prompt updated to:

Do NOT perform calculations. Use tool output only.

🚀 Impact

No infinite loops

Stable execution

Faster responses

🧩 7️⃣ Infinite Iterations / Timeout Error
❌ Error
litellm.Timeout: Connection timed out after 600 seconds
🔎 Cause

Agent looping

Large document passed to LLM

Excessive reasoning steps

✅ Fixes

Reduced max_iter

Structured tool output

Prevented hallucination loops

Removed RPM limits

🚀 Impact

Stable under 5–10 seconds

No timeouts

🧩 8️⃣ Multi-Agent Architecture Not Integrated
❌ Original Issue

Multiple agents defined but only one used.

✅ Fix

Integrated:

verifier

financial_analyst

risk_assessor

investment_advisor

Into sequential Crew pipeline.

🚀 Impact

True multi-agent execution achieved.

🧩 9️⃣ Hardcoded Financial Phrases (Not Generalized)
❌ Issue

Tool worked only for Tesla-like format.

✅ Fix

Added generalized metric detection:

TARGET_METRICS = {
    "revenue": ["total revenue", "total revenues"],
    "net_income": ["net income", "net earnings"],
    ...
}

Case-insensitive matching + regex extraction.

🚀 Impact

Works for:

Annual reports

Quarterly reports

Earnings presentations

Different financial formats

🧩 🔟 Risk Agent Hallucinating Risks
❌ Original Prompt Encouraged Fabrication

Risk agent created generic fake risks.

✅ Fix

Updated instructions:

Only extract risks explicitly mentioned

If none found → state clearly

🚀 Impact

More controlled output.

📈 Final System Capabilities

✔ Upload financial PDFs
✔ Extract structured metrics
✔ Compute margins
✔ Multi-agent workflow
✔ JSON structured response
✔ Fast execution
✔ No hallucinated numbers

⚙ Setup Instructions
1️⃣ Install Dependencies
pip install -r requirement.txt
2️⃣ Install Ollama

Download from:
https://ollama.com

Pull model:

ollama pull mistral

Start Ollama:

ollama run mistral
3️⃣ Run FastAPI Server
uvicorn main:app --reload
🌐 API Documentation

After running:

Visit:

http://127.0.0.1:8000/docs
📌 Endpoint: POST /analyze
Request

file: PDF file (required)

query: optional string

Example cURL
curl -X 'POST' \
  'http://127.0.0.1:8000/analyze' \
  -F 'file=@sample.pdf;type=application/pdf' \
  -F 'query=Analyze this financial document'
Response
{
  "status": "success",
  "analysis": "...",
  "file_processed": "sample.pdf"
}
🏁 Final Outcome

This debugging process:

Identified architectural flaws

Fixed LLM initialization

Fixed file handling

Fixed Pydantic validation

Eliminated hallucinations

Stabilized tool-based extraction

Integrated multi-agent architecture

Prevented infinite loops and timeouts

The system now runs reliably and produces structured financial analysis.
