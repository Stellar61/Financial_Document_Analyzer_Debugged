## Importing libraries and files
import os,json, re

from crewai.tools import BaseTool
from langchain_community.document_loaders import PyPDFLoader
from crewai_tools import SerperDevTool

from pydantic import BaseModel, Field
from typing import Type, ClassVar, Dict, List

## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool
class FinancialDocumentInput(BaseModel):
    path: str = Field(..., description="Path to the financial PDF document")


class FinancialDocumentTool(BaseTool):
    name: str = "Financial Document Reader"
    description: str = "Extracts key structured financial metrics from any financial PDF document."
    args_schema: Type[BaseModel] = FinancialDocumentInput

    # Generalized keyword mapping
    TARGET_METRICS: ClassVar[Dict[str, List[str]]] = {
        "revenue": ["total revenue", "total revenues", "revenue"],
        "net_income": ["net income attributable", "net income", "net earnings"],
        "operating_income": ["income from operations", "operating income"],
        "gross_profit": ["gross profit"],
        "free_cash_flow": ["free cash flow"],
        "cash_position": [
            "cash and cash equivalents",
            "cash, cash equivalents and investments",
        ],
        "ebitda": ["adjusted ebitda", "ebitda"],
    }

    # -------------------------
    # Clean line safely
    # -------------------------
    def _clean_line(self, line: str) -> str:
        line = re.sub(r"\(\d+\)", "", line)  # remove (1), (2)
        line = re.sub(r"\s+", " ", line)     # normalize spaces
        return line.strip()

    # -------------------------
    # Extract valid financial numbers
    # -------------------------
    def _extract_numbers(self, line: str):
        matches = re.findall(
            r"-?\d[\d,]*\.?\d*\s*(B|M|billion|million)?",
            line,
            re.IGNORECASE,
        )

        values = []

        for match in matches:
            full_match = match[0] if isinstance(match, tuple) else match

        # Better extraction with groups
        matches = re.findall(
            r"(-?\d[\d,]*\.?\d*)\s*(B|M|billion|million)?",
            line,
            re.IGNORECASE,
        )

        for number, unit in matches:
            try:
                value = float(number.replace(",", ""))

                # Ignore percentages (very small values with % nearby)
                if "%" in line:
                    continue

                # Ignore unrealistic small numbers
                if value < 10 and unit is None:
                    continue

                if unit:
                    unit = unit.lower()
                    if unit in ["b", "billion"]:
                        value *= 1000  # convert to millions
                    elif unit in ["m", "million"]:
                        value *= 1

                values.append(value)

            except:
                continue

        return values

    # -------------------------
    # Main execution
    # -------------------------
    def _run(self, path: str) -> str:
        loader = PyPDFLoader(path)
        docs = loader.load()

        extracted_metrics = {}

        for page in docs:
            lines = page.page_content.split("\n")

            for line in lines:
                clean_line = self._clean_line(line)
                lower_line = clean_line.lower()

                for metric_name, keywords in self.TARGET_METRICS.items():

                    # Skip if already found
                    if metric_name in extracted_metrics:
                        continue

                    if any(keyword in lower_line for keyword in keywords):
                        numbers = self._extract_numbers(clean_line)

                        if numbers:
                            # Choose LAST number (usually most recent quarter)
                            extracted_metrics[metric_name] = round(numbers[-1], 2)

        if not extracted_metrics:
            return "NO_RELEVANT_FINANCIAL_DATA_FOUND"
        
        if "revenue" in extracted_metrics:
            revenue = extracted_metrics.get("revenue")

            if revenue and revenue != 0:
                if "operating_income" in extracted_metrics:
                    extracted_metrics["operating_margin_percent"] = round(
                        (extracted_metrics["operating_income"] / revenue) * 100, 2
                    )

                if "net_income" in extracted_metrics:
                    extracted_metrics["net_margin_percent"] = round(
                        (extracted_metrics["net_income"] / revenue) * 100, 2
                    )

                if "ebitda" in extracted_metrics:
                    extracted_metrics["ebitda_margin_percent"] = round(
                        (extracted_metrics["ebitda"] / revenue) * 100, 2
                    )

        return json.dumps(extracted_metrics)
    
## Creating Investment Analysis Tool
class InvestmentTool:
    async def analyze_investment_tool(financial_document_data):
        # Process and analyze the financial document data
        processed_data = financial_document_data
        
        # Clean up the data format
        i = 0
        while i < len(processed_data):
            if processed_data[i:i+2] == "  ":  # Remove double spaces
                processed_data = processed_data[:i] + processed_data[i+1:]
            else:
                i += 1
                
        # TODO: Implement investment analysis logic here
        return "Investment analysis functionality to be implemented"

## Creating Risk Assessment Tool
class RiskTool:
    async def create_risk_assessment_tool(financial_document_data):        
        # TODO: Implement risk assessment logic here
        return "Risk assessment functionality to be implemented"