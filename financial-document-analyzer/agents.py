## Importing libraries and files
import os
from crewai import LLM


from crewai import Agent

from tools import search_tool, FinancialDocumentTool

### Loading LLM
llm = LLM(
    model="ollama/mistral",
    base_url="http://localhost:11434",
    temperature=0.2
)

# Creating an Experienced Financial Analyst agent
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal=(
        "Use the Financial Document Reader tool to extract structured metrics "
        "and return them exactly as provided. "
        "Do NOT perform calculations. "
        "Do NOT recompute margins. "
        "Do NOT derive new numbers."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You are a CFA-certified financial analyst specializing in earnings reports, "
        "financial statements, and corporate performance evaluation."
    ),
    tools=[FinancialDocumentTool()],
    llm=llm,
    max_iter=1,
    allow_delegation=False
)

# Creating a document verifier agent
verifier = Agent(
    role="Financial Document Verifier",
    goal=(
        "Verify whether the uploaded document at {path} is a valid financial report "
        "such as earnings report, quarterly update, annual report, or financial statement."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You are a compliance specialist responsible for verifying financial documents. "
        "You carefully inspect document content before approving it for analysis."
    ),
    llm=llm,
    max_iter=1,
    allow_delegation=False
)


investment_advisor = Agent(
    role="Investment Strategist",
    goal=(
        "Provide an evidence-based investment outlook based strictly "
        "on the financial analysis and risk assessment."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You provide objective investment perspectives grounded in financial data "
        "and risk evaluation."
    ),
    llm=llm,
    max_iter=1,
    allow_delegation=False
)


risk_assessor = Agent(
    role="Financial Risk Analyst",
    goal=(
        "Identify financial and operational risks explicitly mentioned "
        "in the document located at {path}."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You specialize in identifying risk factors from financial reports, "
        "SEC filings, and forward-looking statements."
    ),
    llm=llm,
    max_iter=1,
    allow_delegation=False
)
