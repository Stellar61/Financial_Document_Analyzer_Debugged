## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier, risk_assessor, investment_advisor
from tools import search_tool, FinancialDocumentTool

## Creating a task to help solve user's query
analysis_task = Task(
    description=(
        "Use the Financial Document Reader tool to extract structured financial metrics "
        "from {path}. The tool already calculates margins. "
        "DO NOT calculate anything. "
        "Return the metrics exactly as provided."
    ),
    expected_output=(
        "Return JSON:\n"
        "{\n"
        '  "financial_summary": {...},\n'
        '  "profitability_analysis": {...}\n'
        "}\n"
        "Use margin values exactly as returned by the tool."
    ),
    agent=financial_analyst,
    async_execution=False,
)

## Creating an investment analysis task
investment_task = Task(
    description=(
        "Based on the financial analysis and identified risks, "
        "provide a balanced investment outlook."
    ),
    expected_output=(
        "Return JSON:\n"
        "{\n"
        '  "investment_outlook": "...",\n'
        '  "confidence_level": "Low | Medium | High"\n'
        "}"
    ),
    agent=investment_advisor,
    async_execution=False,
)

## Creating a risk assessment task
risk_task = Task(
    description=(
        "Identify financial and operational risks mentioned in the document at {path}."
    ),
    expected_output=(
        "Return JSON:\n"
        "{\n"
        '  "risk_factors": ["..."]\n'
        "}"
    ),
    agent=risk_assessor,
    async_execution=False,
)

    
verification_task = Task(
    description=(
        "Read the document at {path}. "
        "Determine whether it is a financial report. "
        "If it is not a financial document, clearly state why."
    ),
    expected_output="A short confirmation stating whether the document is a financial report.",
    agent=verifier,
    async_execution=False,
)