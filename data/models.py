from typing import Literal
from pydantic import BaseModel


class Candidate(BaseModel):
    first_name:str
    last_name:str
    email:str
    skills:list[str]


class QdrantInputCandidate(BaseModel):
    """Used as arg for insertion in the db"""
    first_name:str
    last_name:str

    #for vectorization
    profile_summary:str
    industry_summary:str
    core_skills_summary:str
    core_soft_skills_summary:str

    #precisse_extracts
    years_of_experience:int
    highest_education:Literal["Bachelor", "Master", "PhD"]
    industry_sectors:str
    skills:str
    tehnologies_used:str
