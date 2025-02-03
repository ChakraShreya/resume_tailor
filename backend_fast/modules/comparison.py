from typing import Dict, List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer


class SemanticSimilarityCalc:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def generate_embeddings(self, text: str) -> np.ndarray:
        return self.model.encode([text])[0]

    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))


class ComparisonAgent:
    def __init__(self):
        self.similarity_calc = SemanticSimilarityCalc()
        self.similarity_threshold = 0.7

    async def compare_keywords(self, resume_keywords: Dict, jd_keywords: Dict) -> Dict:
        matches = []
        missing_skills = []

        # Compare technical skills
        jd_tech = jd_keywords.get("skills", {}).get("tech", {})
        resume_tech = resume_keywords.get("skills", {}).get("tech", [])

        for jd_skill in jd_tech.get("required", []):
            best_match = None
            best_score = 0

            for resume_skill in resume_tech:
                embedding1 = self.similarity_calc.generate_embeddings(jd_skill)
                embedding2 = self.similarity_calc.generate_embeddings(resume_skill)
                score = self.similarity_calc.calculate_similarity(embedding1, embedding2)

                if score > best_score and score > self.similarity_threshold:
                    best_score = score
                    best_match = (jd_skill, resume_skill, score)

            if best_match:
                matches.append(best_match)
            else:
                missing_skills.append(jd_skill)

        return {
            "matches": matches,
            "missing_skills": missing_skills
        }