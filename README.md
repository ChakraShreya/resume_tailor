# resume_tailor

A multi-agent system designed to automate the process of tailoring resumes to match job descriptions. By analyzing an individual’s projects, work experience, and skills, the system generates a resume that highlights the intersections with a given job posting—thereby increasing the candidate's chances of getting shortlisted for an interview.

---

## Table of Contents

- [Overview](#overview)
- [Commands to Run](#commands-to-run)
- [Features](#features)
- [How It Works](#how-it-works)
  

---

## Overview

Job seekers often need to manually adjust their resumes to align with specific job descriptions. This project automates that process by:

- **Extracting key information** from both the job description (JD) and the candidate’s resume.
- **Mapping skills and qualifications** , finding mismatched skills and their use cases in the real world.
- **Providing feedback** on areas where the resume can be enhanced to meet industry trends (for example, suggesting an upgrade from JavaScript to Typescirpt in a UI role).
- **Generating a final, formatted resume** in .md format that emphasizes the most relevant qualifications and projects for the targeted job.

---
## Commands to Run 
- To run the **Backend**
   ```bash
   cd backend_fast
   uvicorn app.main:app --reload
   ```

- To run the **Frontend**
  ```bash
  cd frontend
  npm start
  ```

---
## Features

- **PDF Parsing:** Converts extracted text from the pdfs into a structured JSON format that includes sections such as qualifications and skills (both technical and behavioral).
- **Fit Score Computation:** Calculates a comprehensive “Fit Score” that gives weight to both required and preferred skills, thereby quantifying how well the resume matches the JD.
- **Feedback Generation:** Provides actionable suggestions (e.g., adding new technologies, enhancing existing skills) to improve resume relevancy.
- **Resume Generation:** Final resume based on upgrades accepted by the customer.

---

## How It Works

1. **Parsing:**
   - **PDFparser:** Extracts raw text from PDF files.
   - **ResumeParser & JDParser:** Converts PDF content into structured JSON format.
   - **ParserFactory:** Determines the appropriate parser based on file type.
   - Break down the JD into components such as introductory qualifications, required skills, preferred skills, and responsibilities.
   - Similarly, map the resume into sections like education (qualifications), technical skills, and behavioral skills.

3. **ComparisonAgent:**
   - Compares keywords from the resume and JD creating a list of matched and mismatched skills.
     

5. **Feedback & Enhancement:**
   - **ResearchAgent:** Leverages tools (e.g., the SerperDev API) to fetch industry-relevant use cases and alternative technologies.
   - **AnalysisAgent:** Uses the key use cases found by the research agent to score the degree of fit and generate feedback for potential resume enhancements.

6. **Final Resume Generation:**
   - **ResumeGeneratorAgent:** Produces a final resume based the feedback the user decides to accept , in a .md file that can be downloaded and edited.


