from crewai import Agent, Task ,Crew
from ..config.config import (AZURE_OPENAI_API_KEY,AZURE_OPENAI_ENDPOINT,AZURE_DEPLOYMENT_NAME,AZURE_API_VERSION)
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

def create_analysis_task(skills, use_cases):
    print('Creating analysis task')
    return Task(
        description=(
            f"Here's a mapping of tech to it's use cases:\n{use_cases}\n\n"
            f"Here's a list of all the skills that were matched : {skills["matched_skills"]}\n"
            f"Here's a list of skills that were mismatched : {skills["missing_skills"]}\n"
            f"Analyze the matched skills and the degree of similarity between the mismatched skills to generate a score between 0-100."
            f"Look carefully at the mismatched skills to determine if the candidate's current skills are similar to any of the Job Description(JD) skills and return them as feedback asking the user to upgrade user's skill to the one mentioned in Job Description.\n"
            f"Generate a DICTIONARY(NO EXTRA SENTENCES) with score from 0-100 based on the skill alignment and return feedback ONLY IF some skills are similar between the ones mismatched based on the use case mapping suggesting for upgrades.\n\n"
            f"IMPORTANT: Return ONLY a valid JSON object with exactly this structure:\n"
            f'''{{
                "score": <integer between 0-100>,
                "feedback": [
                    "Upgrade your skill in '<current_skill>' to <target_skill" as they are used for <commonality in use cases>"
                ]
            }}'''
            f"\n\nExample output:\n"
            '''{"score":10,"feedback": ["Upgrade your skill in 'GoLang' as it will help you in 'Building scalable microservices', 'Efficient concurrency handling', and 'Developing cloud-native applications'","Learn 'TypeScript'. It adds to 'Enhancing JavaScript code with static typing', 'Developing Large-scale, maintainable applications', and 'Improving code reliability and refactoring efficiency'"]}'''
        ),
        expected_output="A JSON object with 'score' (integer) and 'feedback' (array of strings) keys, NO EXTRA content before or after",
        agent=analysis_agent
    )

if __name__ == "__main__":
    skills = {"matched_skills":["python","aws"],"missing_skills":{"resume":['javascript','NLTK', 'Git', 'Docker'],"jd":['typescript','GoLang', 'Computer algorithms']}}

    use_cases_mock = {
        "GoLang": [
            "Building scalable microservices",
            "Efficient concurrency handling",
            "Developing cloud-native applications"
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

    task = create_analysis_task(skills, use_cases_mock)
    crew = Crew(agents=[analysis_agent], tasks=[task])  # ✅ Crew Setup
    result = crew.kickoff()

    print("✅ Analysis Result:", result)
