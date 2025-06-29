from typing import Literal
from pydantic import BaseModel


class Candidate(BaseModel):
    first_name:str
    last_name:str
    email:str
    skills:list[str]


class QdrantInputCandidate(BaseModel):
    first_name:str
    last_name:str

    #for vectorization (similarity search)
    profile_summary:str
    industry_summary:str
    core_skills_summary:str
    core_soft_skills_summary:str

    #precise_extracts (SQL-like matching)
    years_of_experience:int
    highest_education:Literal["Bachelor", "Master", "PhD", "None"]
    industry_sectors:str
    skills:str
    tehnologies_used:str

class QdrantPointCandidatePayload(BaseModel):
    first_name:str
    last_name:str

    years_of_experience:int
    highest_education:int
    industry_sectors:str
    skills:str
    tehnologies_used:str

class QdrantPointCandidateVectors(BaseModel):
    profile_summary:list[float]
    industry_summary:list[float]
    core_skills_summary:list[float]
    core_soft_skills_summary:list[float]

class QdrantPointCandidate(BaseModel):
    """Used as arg for insertion in the db"""
    payload:QdrantPointCandidatePayload
    vectors:QdrantPointCandidateVectors

class JobMatchingCriteria(BaseModel):
    min_xp_years:int | None = None
    max_xp_years:int | None = None
    min_education:int | None = None #TODO: unify the level currently in the embed function of the candidate
    mandatory_industry_sector:str
    job_summary:list[float] #embedded job summary

# For the API inputs 
# TODO: transfer to a dedicated file under app/models for exp
class CandidatePayload(BaseModel):
    first_name: str
    last_name: str
    birthdate: str
    age:int
    email:str
    phone:str
    address: str
    skills: list[str]
    experiences: list[dict[str,str|None|int]]
    education: list[dict[str,str|int|None]]

class BudgetPayload(BaseModel):
    min: int | None
    max: int | None
    currency: str


class JobPayload(BaseModel):
    job_title: str
    job_description: str
    budget: BudgetPayload
    location: str
    company_name: str
    employment_type: str
    required_skills: list[str]