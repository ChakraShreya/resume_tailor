from crewai import Agent, Task, Crew
from ..config.config import (AZURE_OPENAI_ENDPOINT, AZURE_DEPLOYMENT_NAME, AZURE_API_VERSION)
import os
import json


os.environ["AZURE_API_BASE"] = AZURE_OPENAI_ENDPOINT
os.environ["AZURE_DEPLOYMENT_NAME"] = AZURE_DEPLOYMENT_NAME
os.environ["AZURE_API_VERSION"] = AZURE_API_VERSION

deployment_name = 'dwx-qe-llm'

resume_gen_agent = Agent(
    role='Resume Generation Expert',
    goal='Generate an optimized resume based on accepted feedback and job requirements.',
    backstory='''You are an expert resume writer who specializes in tailoring resumes to match job descriptions.
    You understand how to highlight relevant skills and experiences while maintaining authenticity.''',
    verbose=True,
    memory=True,
    llm=f"azure/{deployment_name}"
)

def create_resume_gen_task(resume_content: str, jd_content: str, accepted_feedbacks: list):
    print('Creating resume generation task')
    return Task(
        description=(
            f"Generate an optimized resume in markdown format based on the following inputs:\n\n"
            f"Original Resume:\n{resume_content}\n\n"
            f"Job Description:\n{jd_content}\n\n"
            f"Accepted Feedback Items: {json.dumps(accepted_feedbacks, indent=2)}\n\n"
            f"Instructions:\n"
            f"1. Update the technical skills section based on accepted feedback\n"
            f"2. Highlight experiences that align with the job requirements\n"
            f"3. Use markdown formatting for better readability\n"
            f"4. Maintain a professional tone\n"
            f"5. Include all sections from the original resume\n"
            f"6. Add a summary section highlighting key alignments with the job\n"
            f"7. Format technical skills to emphasize matches with JD requirements"
        ),
        expected_output=(
            "A complete resume in markdown format with all sections properly formatted. "
            "The output should be ready to save as a .md file."
        ),
        agent=resume_gen_agent
    )

def parse_generated_resume(result):
    """Helper function to ensure the result is properly formatted"""
    try:
        if isinstance(result, str):
            # Clean up any potential JSON formatting
            if result.startswith('"') and result.endswith('"'):
                result = json.loads(result)
            return result
        elif isinstance(result, dict):
            return json.dumps(result, indent=2)
        else:
            return str(result)
    except Exception as e:
        print(f"Error parsing resume result: {e}")
        return str(result)

if __name__ == "__main__":
    # Test data as raw strings
    resume_mock = """
    John Doe
    john@example.com | 123-456-7890

    SUMMARY
    Experienced software developer with 5 years in web development

    TECHNICAL SKILLS
    - Languages: Python, JavaScript, SQL
    - Frameworks: React, Django
    - Tools: Git, VS Code

    EXPERIENCE

    Senior Developer | Tech Corp | 2020-Present
    - Led team of 5 developers in developing full-stack web applications
    - Implemented CI/CD pipeline reducing deployment time by 40%
    - Developed RESTful APIs using Python and JavaScript

    Software Developer | StartUp Inc | 2018-2020
    - Built responsive web applications using React and Node.js
    - Optimized database queries improving performance by 30%

    EDUCATION
    BS in Computer Science | Tech University | 2018
    """

    jd_mock = """
    Senior Software Engineer

    We are seeking a Senior Software Engineer to join our growing team.

    Required Skills:
    - Python
    - TypeScript
    - SQL
    - AWS
    - Microservices architecture

    Preferred Skills:
    - Docker
    - Kubernetes
    - CI/CD experience

    Responsibilities:
    - Design and implement scalable software solutions
    - Lead technical projects and mentor junior developers
    - Collaborate with cross-functional teams
    """

    accepted_feedbacks_mock = [
        {
            "id": 1,
            "text": "Upgrade JavaScript skills to TypeScript for better alignment with the role",
            "accepted": True
        },
        {
            "id": 2,
            "text": "Add Docker and AWS to technical skills section",
            "accepted": True
        },
        {
            "id": 3,
            "text": "Highlight microservices experience in work history",
            "accepted": True
        }
    ]

    # Test the resume generation
    try:
        task = create_resume_gen_task(resume_mock, jd_mock, accepted_feedbacks_mock)
        crew = Crew(agents=[resume_gen_agent], tasks=[task])
        result = crew.kickoff()

        # Parse and format the result
        formatted_resume = parse_generated_resume(result)

        print("\n=== Generated Resume ===\n")
        print(formatted_resume)

        # Save to file
        with open("generated_resume.md", "w") as f:
            f.write(formatted_resume)
        print("\nResume saved to generated_resume.md")

    except Exception as e:
        print(f"Error generating resume: {e}")

if __name__ == "__main__":
    resume_mock = """
    John Doe
    john@example.com | 123-456-7890

    SUMMARY
    Experienced software developer with 5 years in web development

    TECHNICAL SKILLS
    - Languages: Python, JavaScript, SQL
    - Frameworks: React, Django
    - Tools: Git, VS Code

    EXPERIENCE

    Senior Developer | Tech Corp | 2020-Present
    - Led team of 5 developers in developing full-stack web applications
    - Implemented CI/CD pipeline reducing deployment time by 40%
    - Developed RESTful APIs using Python and JavaScript

    Software Developer | StartUp Inc | 2018-2020
    - Built responsive web applications using React and Node.js
    - Optimized database queries improving performance by 30%

    EDUCATION
    BS in Computer Science | Tech University | 2018
    """

    jd_mock = """
    Senior Software Engineer

    We are seeking a Senior Software Engineer to join our growing team.

    Required Skills:
    - Python
    - TypeScript
    - SQL
    - AWS
    - Microservices architecture

    Preferred Skills:
    - Docker
    - Kubernetes
    - CI/CD experience

    Responsibilities:
    - Design and implement scalable software solutions
    - Lead technical projects and mentor junior developers
    - Collaborate with cross-functional teams
    """

    accepted_feedbacks_mock = [
        {
            "id": 1,
            "text": "Upgrade JavaScript skills to TypeScript for better alignment with the role",
            "accepted": True
        },
        {
            "id": 2,
            "text": "Add Docker and AWS to technical skills section",
            "accepted": True
        },
        {
            "id": 3,
            "text": "Highlight microservices experience in work history",
            "accepted": True
        }
    ]

    try:
        task = create_resume_gen_task(resume_mock, jd_mock, accepted_feedbacks_mock)
        crew = Crew(agents=[resume_gen_agent], tasks=[task])
        result = crew.kickoff()

        formatted_resume = parse_generated_resume(result)

        print("\n=== Generated Resume ===\n")
        print(formatted_resume)

        with open("generated_resume.md", "w") as f:
            f.write(formatted_resume)
        print("\nResume saved to generated_resume.md")

    except Exception as e:
        print(f"Error generating resume: {e}")
