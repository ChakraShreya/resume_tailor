from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
from typing import Dict, List
from dotenv import load_dotenv
import os
import json
import asyncio

load_dotenv()


class TechUseCaseAgent:
    def __init__(self):
        if not os.getenv("SERPER_API_KEY"):
            raise ValueError("SERPER_API_KEY not found in environment variables")

        self.search_tool = SerperDevTool(
            api_key=os.getenv("SERPER_API_KEY"),
            n_results=3
        )

    async def get_tech_descriptions(self, resume_skills: List[str], jd_skills: List[str]) -> Dict:
        tech_descriptions = {"resume": {}, "jd": {}}

        # Process resume skills
        for skill in resume_skills:
            search_results = await asyncio.to_thread(
                lambda: self.search_tool.run(query=f"What is '{skill}' used for in software engineering?")
            )

            summary = await self._summarize_use_case(search_results)
            tech_descriptions["resume"][skill] = summary

        # Process JD skills
        for skill in jd_skills:
            search_results = await asyncio.to_thread(
                lambda: self.search_tool.run(query=f"What is '{skill}' used for in software engineering?")
            )

            summary = await self._summarize_use_case(search_results)
            tech_descriptions["jd"][skill] = summary

        return tech_descriptions

    async def _summarize_use_case(self, search_results: str) -> str:
        summarizer_agent = Agent(
            role="Tech Expert",
            goal="Provide concise, clear explanations of technology use cases",
            backstory="You are an expert at explaining complex technical concepts clearly and concisely.",
        )

        summarize_task = Task(
            description=f"Summarize: {search_results}\nFocus on industry use cases in one sentence.",
            expected_output="A single sentence explaining the technology’s primary use in software engineering.",
            agent=summarizer_agent
        )

        crew = Crew(agents=[summarizer_agent], tasks=[summarize_task])
        results = crew.kickoff()
        return results[0]  # Extract result from task execution


async def test():
    agent = TechUseCaseAgent()
    resume_skills = ["JavaScript", "Python 2"]
    jd_skills = ["TypeScript", "Python 3"]
    results = await agent.get_tech_descriptions(resume_skills, jd_skills)

    print("\nFinal Results:")
    print(json.dumps(results, indent=2))


# Run test safely
if __name__ == "__main__":
    try:
        asyncio.run(test())
    except RuntimeError:
        # If already running inside an event loop (e.g., Jupyter Notebook), use:
        asyncio.create_task(test())
