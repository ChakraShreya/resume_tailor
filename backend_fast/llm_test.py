from openai import AzureOpenAI
import json
import os

resume='''Shreya Chakraborty
Programming Languages : Python, SQL, R, C++, Java
Libraries & Frameworks : PyTorch, TensorFlow, Keras , NumPy, Pandas, Scikit-learn, Garak, Langchain, Stable-Baselines, OpenCV, NL TK,
Git, Docker
EXPERIENCE
Data Science Intern June 2024 – July 2024
Symphony AI Bangalore, India
•Introduced a LLM vulnerability scanner for the Eureka GenAI Platform, identifying and mitigating 80% of potential issues caused
by prompt injection attacks.
•Engineered a prompt-based hallucination detection to generate a conﬁdence score for the LLM output summary, clearly
identifying information that needs veriﬁcation.
•Mitigated hallucination using techniques from NVIDIA Nemo guardrails, reducing hallucination in responses by 40%.
•Collaborated with cross-functional teams to incorporate these methods into models used in ﬁnancial risk analysis and retail
business analysis, enhancing model reliability by 25%.
Research Intern June 2023 – Aug 2023
PES Innovation Lab Bangalore, India
•Conducted research on multi-agent reinforcement learning algorithms for trafﬁc optimization, achieving a 15% improvement in
trafﬁc ﬂow efﬁciency.
•Addressed the curse of dimensionality by developing scalable solutions for larger networks with multiple intersections, resulting
in a 20% reduction in computational complexity.
•Presented ﬁndings at weekly research meetings and documented the team’s work in a LaTeX report.
PROJECTS
Justice Justiﬁed Feb 2024 – Present
Deep Learning, Explainability Huggingface, PyTorch, WanDB, SHAP
•Large scale BERT-like encoder trained to predict the IPC sections cited for over 60,000 Supreme Court and High Court cases.
•Achieved state of the art performance with a macro averaged precision of 59.3%.
•Added explainability for decoding the black box system and eliminating scope for any bias.
Misinformation Detection Agent June 2024 – July 2024
Deep Learning, Blockchain Python, PyTorch, NL TK, OpenCV
•Trained an agent to dynamically orchestrate tools based on the incoming multi-modal news, improving detection accuracy by 30%
on the benchmark FakeNewsNet dataset. Used advanced deep learning techniques and ensemble methods for accurate detection.
•Designed tools such as Deepfake Detectors, Keyframe Extractor, Similarity Checker, and Source Tracker, which analyze news
websites and provide an immediate score, reducing analysis time by 50%. Leveraged OpenCV for image and video processing, and
NL TK along with prompt engineering-based methods for comprehensive text analysis and context extraction.
•Integrated a blockchain network for consensus-based decision-making by validators, increasing system transparency and
reliability by 20%. Designed and implemented smart contracts to ensure data integrity and validator accountability.
EDUCATION
PES University Bangalore, India
B.Tech in Computer Science, CGPA (up to 6th semester): 9.34/10 Jan 2022 – Present
The Deens Academy Bangalore, India
12th grade score: 96.6% June 2019 – March 2021
Narayana E-Techno School Bangalore, India
10th grade score: 93.4% June 2014 – March 2019
'''
resume_prompt = f"""
Resume:
{resume}

Extract information from this resume,reading through each section carefully like introduction, work experience and projects, and format it as JSON with the following structure:
{{
    "qualifications": [list of educational qualifications],
    "skills": {{
        "tech": [list of technical skills],
        "behav": [list of behavioral/soft skills]
    }}
}}
Only include factual information present in the resume.

ex:
{{
            "qualifications": [
                "B.Tech in Computer Science, PES University, CGPA (up to 6th semester): 9.34/10",
                "12th grade score: 96.6%, The Deens Academy"
            ],
            "skills": {{
                "tech": [
                    "Python", 
                    "SQL", 
                    "R", 
                    "C++"
                ],
                "behav": [
                    "Collaboration with cross-functional teams",
                    "Research and presentation in weekly meetings"
                ]
            }}
        }}

"""

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint="https://dwx-qe-open-ai-canadaeast.openai.azure.com"
)

deployment_name = 'dwx-qe-llm'

# Send a completion call to generate an answer
print('Sending a test completion job')

response = client.chat.completions.create(
    model=deployment_name,
    messages=[{"role": "user", "content": resume_prompt}]
)
print(response.choices[0].message.content)