from celery_worker import celery_app
from crewai import Crew, Process
from agents import financial_analyst, verifier, risk_assessor, investment_advisor
from task import verification_task, analysis_task, risk_task, investment_task
import os


@celery_app.task(name="tasks.analyze_document_task")
def analyze_document_task(query: str, file_path: str, file_name: str):

    financial_crew = Crew(
        agents=[verifier, financial_analyst, risk_assessor, investment_advisor],
        tasks=[verification_task, analysis_task, risk_task, investment_task],
        process=Process.sequential,
    )

    result = financial_crew.kickoff(
        inputs={
            "query": query,
            "path": file_path
        }
    )

    # Cleanup file after processing
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except:
            pass

    return str(result)