from crewai import Agent, Task,Crew
from config.config import (AZURE_OPENAI_ENDPOINT,AZURE_DEPLOYMENT_NAME,AZURE_API_VERSION)
import os
import json
# import litellm
# from openai import AzureOpenAI
# from litellm import completion


# print(AZURE_API_VERSION,AZURE_OPENAI_ENDPOINT,AZURE_DEPLOYMENT_NAME)
# os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY
os.environ["AZURE_API_BASE"] = AZURE_OPENAI_ENDPOINT
os.environ["AZURE_DEPLOYMENT_NAME"] = AZURE_DEPLOYMENT_NAME
os.environ["AZURE_API_VERSION"] = AZURE_API_VERSION

print(os.getenv("AZURE_API_BASE"))
print(os.getenv("AZURE_DEPLOYMENT_NAME"))
print(os.getenv("AZURE_API_VERSION"))

deployment_name = 'dwx-qe-llm'

# response = completion(
#     model = f"azure/{deployment_name}",
#     messages = [{ "content": "Hello, how are you?","role": "user"}]
# )
# print(response)

# try:
#     client=AzureOpenAI(api_version=AZURE_API_VERSION,azure_endpoint=AZURE_OPENAI_ENDPOINT)
#     response = client.chat.completions.create(
#         messages=[{"role": "user", "content": "which gpt model are you specifically"}],
#         model=deployment_name
#     )
#     print(response.to_json())
# except Exception as e:
#     print(f"Direct OpenAI SDK Error: {e}")

# os.environ['LITELLM_LOG'] = 'DEBUG'
# litellm.set_verbose=True

comparison_agent = Agent(
    role='Resume-JD Comparison Expert',
    goal='Identify technical skill gaps between a resume and a job description.',
    backstory='You specialize in comparing resumes with job descriptions to detect skill mismatches.',
    verbose=True,
    memory=True,
    llm= f"azure/{deployment_name}"
)

def create_comparison_task(resume, jd):
    print('Creating comparison task')
    return Task(
        description=(
            f"Compare the following resume and job description to identify compare technical skills:\n\n"
            f"Resume: {resume.get('skills',{}).get('tech',[])}\n"
            f"Job Description: {jd.get('skills', {}).get('tech', {}).get('required', [])}\n\n"
            f"Strictly return only a Dictionary (NO EXTRA SENTENCES) of all technical skills that are mismatched in the resume and JD(with the keys being 'resume' and 'jd'), and another dictionary of matches."
        ),
        expected_output='A JSON of the form :{"matched_skills":[],"missing_skills":{"resume":[],"jd":[]}}',
        agent=comparison_agent,
    )
if __name__ == "__main__":
    resume_mock = {
        "skills": {"tech": ["Python", "SQL"], "behav": ["Teamwork"]}
    }
    jd_mock = {
        "skills": {"tech": {"required": ["Python", "GoLang", "SQL"], "preferred": ["TensorFlow"]}}
    }

    task = create_comparison_task(resume_mock, jd_mock)
    crew = Crew(agents=[comparison_agent], tasks=[task])
    result = crew.kickoff()

    print(json.dumps(result.raw, indent=4))
    # print(f"Raw Output: {type(result.raw)}")
    # if result.json_dict:
    #     print(f"JSON Output: {json.dumps(result.json_dict, indent=2)}")
    # if result.pydantic:
    #     print(f"Pydantic Output: {result.pydantic}")
    # print(f"Tasks Output: {result.tasks_output}")
    # print(f"Token Usage: {result.token_usage}")