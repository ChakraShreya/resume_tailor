from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
import io
from fastapi.middleware.cors import CORSMiddleware
import json
# import PyPDF2
# from docx import Document
import numpy as np
from modules.parser import ParserFactory
from agents.comparison_agent import create_comparison_task,comparison_agent
from agents.research_agent import create_research_task,research_agent
from agents.analysis_agent import create_analysis_task,analysis_agent
from crewai import Crew, Process

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

feedback_store=[]

# comparison_agent = ComparisonAgent()
@app.get("/")
async def read_root():
    return {"message": "Welcome to Resume Tailor "}

class Feedback(BaseModel):
    id: int
    text: str
    accepted: bool | None = None


@app.post("/analyze")
async def analyze_resume_and_jd(resume: UploadFile = File(...), jd: UploadFile = File(...)):
    try:
        # Step 1: Parse resume and JD
        resume_parser = ParserFactory.get_parser("resume")
        jd_parser = ParserFactory.get_parser("jd")

        resume_content = await resume.read()
        resume_json = await resume_parser.parse_to_json(resume_content)
        print(resume_json)

        jd_content = await jd.read()
        jd_json = await jd_parser.parse_to_json(jd_content)
        print(jd_json)

        print("\n🔄 DEBUG: Creating comparison task")
        comparison_task = create_comparison_task(resume_json, jd_json)

        print("\n🔍 DEBUG: Extracted Skills:")
        print(f"Resume Skills: {resume_json.get('skills', {}).get('tech', [])}")
        print(f"JD Required Skills: {jd_json.get('skills', {}).get('tech', {}).get('required', [])}")
        print(f"JD Preferred Skills: {jd_json.get('skills', {}).get('tech', {}).get('preferred', [])}")

        if not comparison_task:
            print("\n❌ DEBUG: Failed to create comparison task")
            return {"error": "Invalid resume or job description format"}, 400

        print("\n🚀 DEBUG: Running comparison crew")
        comparison_crew = Crew(
            agents=[comparison_agent],
            tasks=[comparison_task]
        )
        comparison_result = comparison_crew.kickoff().raw
        print(comparison_result)
        comparison_result=json.loads(comparison_result)
        print(f"\n✅ DEBUG: Comparison Result:")
        print(json.dumps(comparison_result, indent=4))

        #save serper
        comparison_result={"matched_skills":["Python","Java"],"missing_skills":{"resume":['javascript', 'Git', 'Docker'],"jd":['typescript','GoLang']}}
        # Step 2: Research missing skills
        missing_skills_list = comparison_result.get('missing_skills', {}).get('resume',[]) + comparison_result.get('missing_skills', {}).get('jd',[])
        print(f"\n🔍 DEBUG: Missing Skills: {missing_skills_list}")

        # if missing_skills_list:
        #     print("\n🔄 DEBUG: Creating research task")
        #     research_task = create_research_task(missing_skills_list)
        #     research_crew = Crew(
        #         agents=[research_agent],
        #         tasks=[research_task]
        #     )
        #     use_cases = json.loads(research_crew.kickoff().raw)
        #     print(f"\n✅ DEBUG: Research Results:")
        #     print(json.dumps(use_cases, indent=2))
        # else:
        #     use_cases = {}
        #     print("\n📝 DEBUG: No missing skills to research")

        # save serper
        use_cases={
            "javascript": [
                "Used for website front-end development.",
                "Applied in creating in-browser games.",
                "Implemented on NodeJS for backend web frameworks."
            ],
            "Git": [
                "Utilized for managing multiple branches with diverging codebases.",
                "Used to track and manage changes to source code and text files.",
                "Allows teams to work together using the same files."
            ],
            "Docker": [
                "Used for creating a consistent environment for deploying applications.",
                "Employed for faster configuration with consistency.",
                "Used for better disaster recovery."
            ],
            "typescript": [
                "Utilized for backend web development.",
                "Used in mobile applications development.",
                "Implemented in library or framework development to provide clear interfaces."
            ],
            "GoLang": [
                "Used for cross-platform desktop apps development.",
                "Implemented for low-level networking.",
                "Applied in server-side apps and in various web services."
            ]
        }

        # Step 3: Analyze alignment
        print("\n🔄 DEBUG: Creating analysis task")
        analysis_task = create_analysis_task(comparison_result.get('missing_skills',[]), use_cases)
        analysis_crew = Crew(
            agents=[analysis_agent],
            tasks=[analysis_task]
        )
        print("\n🚀 DEBUG: Running analysis crew")
        analysis_result = json.loads(analysis_crew.kickoff().raw)
        print(f"\n✅ DEBUG: Analysis Result:")
        print(json.dumps(analysis_result, indent=2))

        # Format response
        try:
            score = analysis_result.get('score', 0)
            feedback = analysis_result.get('feedback', [])

            formatted_feedback = [
                {"id": idx + 1, "text": fb, "accepted": None}
                for idx, fb in enumerate(feedback)
            ]

            print("\n✅ DEBUG: Final Response:")
            print(json.dumps({
                "score": score,
                "feedback": formatted_feedback
            }, indent=2))

            return {
                "score": score,
                "feedback": formatted_feedback
            }

        except Exception as e:
            print(f"\n❌ DEBUG: Error formatting response: {str(e)}")
            return {"error": f"Error formatting analysis results: {str(e)}"}, 400
    except Exception as e:
        return {"error": str(e)}, 400


# Generate a resume based on the feedbacks
@app.post("/generate_resume")
async def generate_resume(feedbacks: str=Form(...), resume: UploadFile = File(...), jd: UploadFile = File(...)):
    # Here you would process the feedback and generate a tailored resume
    parsed_feedbacks = [Feedback(**item) for item in json.loads(feedbacks)]
    #CODE parser for resume and jd
    resume_content = await resume.read()
    jd_content = await jd.read()
    print(parsed_feedbacks)

    # Simulate the resume generation
    mock_resume = f"""
    # Resume Tailored to Job Description

    ### Summary
    - Metrics added to achievements.
    - Relevant keywords incorporated.

    ### Skills
    - Leadership roles emphasized.
    - Expanded technical skills.

    ### Certifications
    - Added recent certifications.

    ---
    Generated using Resume Tailor. Score: 85 
    """
    return {"resume": mock_resume}
