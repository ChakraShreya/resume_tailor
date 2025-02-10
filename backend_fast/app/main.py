from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import json
# import PyPDF2
# from docx import Document
from .modules.parser import ParserFactory
from .agents.comparison_agent import create_comparison_task,comparison_agent
from .agents.research_agent import create_research_task,research_agent
from .agents.analysis_agent import create_analysis_task,analysis_agent
from .agents.resume_gen_agent import create_resume_gen_task, resume_gen_agent, parse_generated_resume
import re
import asyncio
from crewai import Crew
import asyncio

from fastapi.responses import StreamingResponse
from asyncio import Queue
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

process_logs = []

def log_step(step: str):
    global process_logs
    process_logs.append(step)
    print(f"🔄 log_step: {step}")
    print("log_step ",process_logs)


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
    global process_logs
    process_logs = []
    try:
        # Step 1: Parse resume and JD
        log_step("parsing")

        resume_parser = ParserFactory.get_parser("resume")
        jd_parser = ParserFactory.get_parser("jd")

        resume_content = await resume.read()
        resume_json = await resume_parser.parse_to_json(resume_content)
        print(resume_json)

        jd_content = await jd.read()
        jd_json = await jd_parser.parse_to_json(jd_content)
        print(jd_json)

        log_step(f"Parsing complete - Resume: {json.dumps(resume_json)}")
        log_step(f"Parsing complete - JD: {json.dumps(jd_json)}")

        log_step("Creating comparison task")
        comparison_task = create_comparison_task(resume_json, jd_json)

        if not comparison_task:
            log_step("Error: Failed to create comparison task.")
            return {"error": "Invalid resume or job description format"}, 400

        log_step("Running comparison agent")
        comparison_crew = Crew(
            agents=[comparison_agent],
            tasks=[comparison_task],
            async_mode=True
        )
        comparison_result = await comparison_crew.kickoff_async()

        print("\n\n\n\n")
        print(type(comparison_result))
        print(comparison_result)
        print("\n\n\n\n")

        comparison_result=json.loads(comparison_result.raw)
        log_step(f"Comparison completed - Results: {json.dumps(comparison_result)}")
        print("comparison result: ",json.dumps(comparison_result, indent=4))

        #save serper
        # comparison_result={"matched_skills":["Python","Java"],"missing_skills":{"resume":['javascript', 'Git', 'Docker'],"jd":['typescript','GoLang']}}

        # Step 2: Research missing skills
        missing_skills_list = comparison_result.get('missing_skills', {}).get('resume',[]) + comparison_result.get('missing_skills', {}).get('jd',[])
        log_step(f"missing_skills: {comparison_result.get('missing_skills', {})}")
        print(f"\n🔍 DEBUG: Missing Skills: {missing_skills_list}")
        # missing_skills_list= None #save serper
        if missing_skills_list:
            log_step("Creating research task")
            research_task = create_research_task(missing_skills_list)
            research_crew = Crew(
                agents=[research_agent],
                tasks=[research_task],
                async_mode=True
            )
            use_cases = await research_crew.kickoff_async()
            use_cases=json.loads(use_cases.raw)

            # save serper
            # use_cases={
            #     "javascript": [
            #         "Used for website front-end development.",
            #         "Applied in creating in-browser games.",
            #         "Implemented on NodeJS for backend web frameworks."
            #     ],
            #     "Git": [
            #         "Utilized for managing multiple branches with diverging codebases.",
            #         "Used to track and manage changes to source code and text files.",
            #         "Allows teams to work together using the same files."
            #     ],
            #     "Docker": [
            #         "Used for creating a consistent environment for deploying applications.",
            #         "Employed for faster configuration with consistency.",
            #         "Used for better disaster recovery."
            #     ],
            #     "typescript": [
            #         "Utilized for backend web development.",
            #         "Used in mobile applications development.",
            #         "Implemented in library or framework development to provide clear interfaces."
            #     ],
            #     "GoLang": [
            #         "Used for cross-platform desktop apps development.",
            #         "Implemented for low-level networking.",
            #         "Applied in server-side apps and in various web services."
            #     ]
            # }

            log_step(f"Research completed - Use Cases: {json.dumps(use_cases)}")
        else:
            use_cases = {}
            log_step("No missing skills to research")



        # Step 3: Analyze alignment
        log_step("Creating analysis task")
        analysis_task = create_analysis_task(comparison_result, use_cases)
        analysis_crew = Crew(
            agents=[analysis_agent],
            tasks=[analysis_task],
            async_mode=True
        )
        log_step("Running analysis agent")
        analysis_result = await analysis_crew.kickoff_async()
        analysis_result=analysis_result.raw

        analysis_result=re.search(r'\{.*\}', analysis_result, re.DOTALL)
        if analysis_result:
            analysis_result=json.loads(analysis_result.group())
        else:
            analysis_result={"error": "Invalid analysis result format"}

        log_step("Analysis completed.")

        print("analysis result:",json.dumps(analysis_result, indent=2))

        # Format response
        try:
            score = analysis_result.get('score', 0)
            feedback = analysis_result.get('feedback', [])

            formatted_feedback = [
                {"id": idx + 1, "text": fb, "accepted": None}
                for idx, fb in enumerate(feedback)
            ]

            print("\nDEBUG: Final Response:")
            print(json.dumps({
                "score": score,
                "feedback": formatted_feedback
            }, indent=2))

            log_step("Process completed successfully.")

            return {
                "score": score,
                "feedback": formatted_feedback
            }

        except Exception as e:
            log_step(f"❌ Error: {str(e)}")
            return {"error": f"Error formatting analysis results: {str(e)}"}, 400
    except Exception as e:
        return {"error": str(e)}, 400

def filter_accepted_feedbacks(parsed_feedbacks: List[dict]) -> List[dict]:
    return [f for f in parsed_feedbacks if f.get('accepted')]

# Generate a resume based on the feedbacks
@app.post("/generate_resume")
async def generate_resume(feedbacks: str=Form(...), resume: UploadFile = File(...), jd: UploadFile = File(...)):
    try:
        # Parse feedbacks
        parsed_feedbacks = json.loads(feedbacks)
        accepted_feedbacks = filter_accepted_feedbacks(parsed_feedbacks)

        # Initialize parsers just for text extraction
        resume_parser = ParserFactory.get_parser("resume")
        jd_parser = ParserFactory.get_parser("jd")

        # Get raw content and extract text from PDFs
        resume_content = resume_parser.extract_text(await resume.read())
        jd_content = jd_parser.extract_text(await jd.read())

        print("\n✅ DEBUG: Accepted Feedbacks:")
        print(json.dumps(accepted_feedbacks, indent=2))

        # Generate optimized resume
        task = create_resume_gen_task(resume_content, jd_content, accepted_feedbacks)
        crew = Crew(agents=[resume_gen_agent], tasks=[task])
        result = crew.kickoff()

        # Parse and format the result
        formatted_resume = parse_generated_resume(result)

        return {"resume": formatted_resume}

    except Exception as e:
        print(f"\n❌ DEBUG: Error generating resume: {str(e)}")
        return {"error": str(e)}, 400

@app.get("/logs")
async def get_process_logs():
    """Returns the logs of the ongoing/last analysis process."""
    print("get_process_logs ",process_logs)
    return {"logs": process_logs}
