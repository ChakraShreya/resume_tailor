from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
import io
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
@app.get("/")
async def read_root():
    return {"message": "Welcome to Resume Tailor API"}

class Feedback(BaseModel):
    id: int
    text: str
    accepted: bool | None = None


# Mock score function that simulates processing the uploaded files
@app.post("/score")
async def score_resume_and_jd(resume: UploadFile = File(...), jd: UploadFile = File(...)):
    # Mock score calculation logic
    resume_content = await resume.read()
    print("read resume")
    jd_content = await jd.read()
    print("read jd")

    # Simulate score based on file contents (you can replace with actual scoring logic)
    score = 85  # Mock score

    return {"score": score}


# Mock feedback list based on the resume and job description
@app.get("/feedbacks", response_model=List[Feedback])
async def get_feedbacks():
    feedbacks = [
        {"id": 1, "text": "Add more specific metrics to your achievements.", "accepted": None},
        {"id": 2, "text": "Include more keywords from the job description.", "accepted": None},
        {"id": 3, "text": "Remove irrelevant experience from your resume.", "accepted": None},
        {"id": 4, "text": "Highlight leadership roles in previous jobs.", "accepted": None},
        {"id": 5, "text": "Expand details about your technical skills.", "accepted": None},
        {"id": 6, "text": "Include recent certifications.", "accepted": None},
    ]
    return feedbacks


# Generate a resume based on the feedbacks
@app.post("/generate_resume")
async def generate_resume(feedbacks: str=Form(...), resume: UploadFile = File(...), jd: UploadFile = File(...)):
    # Here you would process the feedback and generate a tailored resume
    parsed_feedbacks = [Feedback(**item) for item in json.loads(feedbacks)]
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
    Generated using Resume Tailor. Score: 85 (based on JD and Resume matching)
    """
    return {"resume": mock_resume}

