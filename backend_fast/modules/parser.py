from typing import Dict, List
from abc import ABC, abstractmethod
import PyPDF2
import io
import json
from pydantic import BaseModel
from config.config import get_azure_client, AZURE_DEPLOYMENT_NAME


class ResumeStructure(BaseModel):
    qualifications: List[str]
    skills: Dict[str, List[str]]

class JDStructure(BaseModel):
    qualifications: List[str]
    skills: Dict[str, Dict[str, List[str]] | List[str]]

class BaseParser(ABC):
    def __init__(self):
        self.prompt_template = self.get_prompt_template()
        self.client = get_azure_client()
        self.deployment_name = AZURE_DEPLOYMENT_NAME

    @abstractmethod
    def get_prompt_template(self) -> str:
        """Return the prompt template specific to each parser type"""
        pass

    def extract_text(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_stream = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def _generate_prompt(self, text: str) -> str:
        """Generate the complete prompt by inserting the text"""
        return self.prompt_template.format(text=text)

    async def get_llm_response(self, prompt: str) -> str:
        """Get response from LLM"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error getting LLM response: {str(e)}")

    @abstractmethod
    async def parse_to_json(self, pdf_input: bytes) -> Dict:
        """Abstract method to be implemented by specific parsers"""
        pass

class ResumeParser(BaseParser):
    def get_prompt_template(self) -> str:
        return """
        Extract information from this resume, reading through each section carefully like introduction, work experience and projects, and format it as JSON with the following structure:
        {{
            "qualifications": [list of educational qualifications],
            "skills": {{
                "tech": [list of technical skills],
                "behav": [list of behavioral/soft skills]
            }}
        }}
        Only include factual information present in the resume.
        If there are skills like "React and Node" mentioned in a point make sure to seperate it in the list as each a string.
        Example output:
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

        Resume text to process:
        {text}
        """

    async def parse_to_json(self, pdf_input: bytes) -> Dict:
        try:
            text = self.extract_text(pdf_input)
            prompt = self._generate_prompt(text)
            response_text = await self.get_llm_response(prompt)
            parsed_data = json.loads(response_text)
            return ResumeStructure(**parsed_data).dict()
        except Exception as e:
            raise Exception(f"Error parsing resume to JSON: {str(e)}")

class JDParser(BaseParser):
    def get_prompt_template(self) -> str:
        return """
        Extract information from this job description and format it as JSON with the following structure:
        {{
            "qualifications": [list of required educational qualifications],
            "skills": {{
                "tech": {{
                    "required": [list of required technical skills],
                    "preferred": [list of preferred/nice-to-have technical skills]
                }},
                "behav": [list of required behavioral/soft skills]
            }}
        }}
        Only include factual information present in the job description.
        If there are skills like "React and Node" or "Typescript/JavaScript" mentioned in a point make sure to seperate it in the list as each a string.
        If there are phrases like "understanding of data structures" or "experience with react.js and redux" extract it as "data structures","react.js","redux". Eliminate these extra words like "understanding of" or "experience in"
        Example output:
        {{
            "qualifications": [
                "Bachelor's degree in Computer Science or related field",
                "Master's degree preferred"
            ],
            "skills": {{
                "tech": {{
                    "required": [
                        "Python",
                        "Machine Learning",
                        "NLP"
                    ],
                    "preferred": [
                        "AWS",
                        "Docker"
                    ]
                }},
                "behav": [
                    "Strong communication skills",
                    "Team player"
                ]
            }}
        }}

        Job Description text to process:
        {text}
        """

    async def parse_to_json(self, pdf_input: bytes) -> Dict:
        try:
            text = self.extract_text(pdf_input)
            prompt = self._generate_prompt(text)
            response_text = await self.get_llm_response(prompt)
            parsed_data = json.loads(response_text)
            return JDStructure(**parsed_data).dict()
        except Exception as e:
            raise Exception(f"Error parsing JD to JSON: {str(e)}")

# Factory class remains the same
class ParserFactory:
    @staticmethod
    def get_parser(parser_type: str) -> BaseParser:
        if parser_type.lower() == "resume":
            return ResumeParser()
        elif parser_type.lower() == "jd":
            return JDParser()
        else:
            raise ValueError(f"Unknown parser type: {parser_type}")