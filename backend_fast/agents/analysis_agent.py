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

def create_analysis_task(missing_skills, use_cases):
    print('Creating analysis task')
    return Task(
        description=(
            f"Here's a mapping of tech to it's use cases:\n{use_cases}\n\n"
            f"Here's a list of skills that were mismatched : {missing_skills}\n"
            f"Determine if the candidate’s current skills are similar to any of the Job Description(JD) skills are return them as feedback asking the user to upgrade user's skill to the one mentioned in Job Description.\n"
            f"Generate a score from 0-100 based on the skill alignment and return feedback only if some skills are similar between the ones mismatched based on the use case mapping suggesting for upgrades."
        ),
        expected_output="Strictly return a JSON with 'score'(score (0-100)) and 'feedback'( a list of feedback suggestions for the candidate.)",
        agent=analysis_agent
    )

if __name__ == "__main__":
    missing_skills = {"resume":['javascript','NLTK', 'Git', 'Docker'],"jd":['typescript','GoLang', 'Computer algorithms']}

    use_cases_mock = {
        "GoLang": [
            "Building scalable microservices",
            "Efficient concurrency handling",
            "Developing cloud-native applications"
        ],
        "Computer algorithms": [
            "Optimizing search and sort operations",
            "Solving complex computational problems",
            "Enhancing data processing efficiency"
        ],
        "NLTK": [
            "Text tokenization and preprocessing",
            "Sentiment analysis on large datasets",
            "Named Entity Recognition (NER)"
        ],
        "Git": [
            "Version control for collaborative development",
            "Managing code repositories in CI/CD pipelines",
            "Tracking and reverting code changes efficiently"
        ],
        "Docker": [
            "Containerizing applications for portability",
            "Automating deployment in cloud environments",
            "Simplifying DevOps workflows with container orchestration"
        ],
        "JavaScript": [
            "Developing interactive web applications",
            "Creating dynamic user interfaces",
            "Building full-stack applications with Node.js"
        ],
        "TypeScript": [
            "Enhancing JavaScript code with static typing",
            "Developing large-scale, maintainable applications",
            "Improving code reliability and refactoring efficiency"
        ]
    }

    task = create_analysis_task(missing_skills, use_cases_mock)
    crew = Crew(agents=[analysis_agent], tasks=[task])  # ✅ Crew Setup
    result = crew.kickoff()

    print("✅ Analysis Result:", result)
