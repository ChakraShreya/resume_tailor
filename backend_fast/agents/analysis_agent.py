from crewai import Agent, Task ,Crew
from config.config import (AZURE_OPENAI_API_KEY,AZURE_OPENAI_ENDPOINT,AZURE_DEPLOYMENT_NAME,AZURE_API_VERSION)
import os

os.environ["AZURE_API_BASE"] = AZURE_OPENAI_ENDPOINT
os.environ["AZURE_DEPLOYMENT_NAME"] = AZURE_DEPLOYMENT_NAME
os.environ["AZURE_API_VERSION"] = AZURE_API_VERSION

deployment_name='dwx-qe-llm'

analysis_agent = Agent(
    role='Skill Alignment Analyst',
    goal='Analyze use cases to assess how well a candidate’s skills align with job requirements.',
    backstory='You help candidates improve their resumes by evaluating how their skills align with job requirements.',
    verbose=True,
    memory=True,
    allow_delegation=True,
    llm=f"azure/{deployment_name}"
)

def create_analysis_task(resume, jd, use_cases):
    print('Creating analysis task')
    return Task(
        description=(
            f"Analyze the following use cases:\n{use_cases}\n\n"
            f"Compare them with the candidate's resume skills:\n{resume['skills']}\n"
            f"Determine if the candidate’s current skills are relevant to these use cases even if they don’t exactly match the job description.\n"
            f"Generate a score from 0-100 based on the skill alignment and provide actionable feedback."
        ),
        expected_output="Strictly return a JSON with 'score'(score (0-100)) and 'feedback'( a list of feedback suggestions for the candidate.)",
        agent=analysis_agent
    )

if __name__ == "__main__":
    resume_mock = {
        "skills": {"tech": ["Python", "SQL"], "behav": ["Teamwork"]}
    }
    jd_mock = {
        "skills": {"tech": {"required": ["Python", "GoLang", "SQL"], "preferred": ["TensorFlow"]}}
    }
    use_cases_mock = {
        "GoLang": ["Backend for microservices", "Concurrency handling", "Cloud applications"],
        "MLFlow": ["Model tracking", "Pipeline automation", "Experiment management"]
    }

    task = create_analysis_task(resume_mock, jd_mock, use_cases_mock)
    crew = Crew(agents=[analysis_agent], tasks=[task])  # ✅ Crew Setup
    result = crew.kickoff()

    print("✅ Analysis Result:", result)
