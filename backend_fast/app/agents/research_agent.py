import os
from crewai import Agent, Task,Crew
from crewai_tools import SerperDevTool
from ..config.config import (AZURE_OPENAI_API_KEY,AZURE_OPENAI_ENDPOINT,AZURE_DEPLOYMENT_NAME,AZURE_API_VERSION)

os.environ["AZURE_API_BASE"] = AZURE_OPENAI_ENDPOINT
os.environ["AZURE_DEPLOYMENT_NAME"] = AZURE_DEPLOYMENT_NAME
os.environ["AZURE_API_VERSION"] = AZURE_API_VERSION

deployment_name = 'dwx-qe-llm'

search_tool = SerperDevTool()

research_agent = Agent(
    role='Tech Research Specialist',
    goal='Research real-world use cases for technical skills.',
    backstory='You are an expert in finding concise, relevant examples of how technical skills are applied in the industry.',
    verbose=True,
    memory=True,
    tools=[search_tool],
    llm= f"azure/{deployment_name}"
)

def create_research_task(missing_skills):
    print("Creating research task...")
    return Task(
        description=(
            f"For each of the following skills listed below, search online for what it is and the top 2 uses in software development:\n"
            f"{', '.join(missing_skills)}\n"
            f"Summarize each use case in one concise line."
        ),
        expected_output="Strictly return a JSON mapping each missing skill as the key to a list of concise use case summaries.",
        agent=research_agent,
        tools=[search_tool]
    )

if __name__ == "__main__":
    missing_skills_mock = ["GoLang", "MLFlow"]
    task = create_research_task(missing_skills_mock)
    crew = Crew(agents=[research_agent], tasks=[task])  # ✅ Crew Setup
    result = crew.kickoff()

    print("✅ Research Results:", result)