from typing import Literal
from config import GOOGLE_CLIENT, MODEL_NAME
from data.models import QdrantInputCandidate
from google.genai import types
from datetime import datetime

def custom_generate_content(prompt: str) -> str:
    "wrapper around Google API"
    _model_config = types.GenerateContentConfig(temperature=1.0)
    response = GOOGLE_CLIENT.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Part.from_text(
                text="You are a synthetic data generator. Give me a random first name and last name for an employee, pick his job (possible profiles are product, sales, backend, frontend, data engineer, fullstack, architect, etc.), describe in 3 lines what he/she does. Provide his/her country, name of colleges attended, and name of companies. Use random companies names (realistic, big or small). Make the name ethnically diverse, use all possible countries including Europe, Africa, USA, Latin America, Asia. Do not use names Anya or Elias"
            )
        ],
        config=_model_config,
    ).text

    return response if response is not None else ""


__PROFILE_SUMMARY_PROMPT = """You are a helpful Human Resource Assistance. Your task is to provide a summary of a candidate for a position at our company.

Bear in mind that you must
- provide a 10-lines max summary
- describe the candidate taking into account its cultural background, education, skills and industry.
- the goal is not to list what is in the json but to provide sound reasoning basis for an HR professional.

Candidate information:
{data}
"""
__INDUSTRY_SUMMARY_PROMPT = """You are a helpful Human Resource Assistance. Your task is to provide a summary of the industries the candidate worked in.

Bear in mind that you must
- provide a list of items separated by semi-columns, initiated such as "insurance; cars; actuary" or "cyber-security; software, start-up".
- extrapolate based on information you have on the companies and resume of the candidate. for example if the candidate is a full-stack engineer, you can automatically deduce that he works in the software industry as well. if he worked in a young startup in the realm of construction works and handles data-engineering, then you can add "construction, startup, building, data, software" for exp. Try to be exhaustive. 
- There could be up to 10 words

Candidate information:
{data}
"""
__CORE_TECHNICAL_SKILLS_SUMMARY_PROMPT = """You are a helpful Human Resource Assistance. Your task is to provide a summary of the core technical skills the candidate has.

Bear in mind that you must
- provide a list of items separated by semi-columns, initiated such as "software architecture; POCs; data-science; scaling" or "sales; growth-hacking; wine; no-code".
- we are not interested in the name of specific technologies. For exemple "python" is not a skill. high-level software programming is. "vue.js" is not a skill, but "frontend" is
- infer skills based on what you read. For example a candidate that has experience setting up FastApi automatically has experience with "backend, scaling, webapp"

Candidate information:
{data}
"""
__CORE_SOFT_SKILLS_SUMMARY_PROMPT = """You are a helpful Human Resource Assistance. Your task is to provide a summary of the core soft skills the candidate has.

Bear in mind that you must
- provide a list of items separated by semi-columns, initiated such as "management; scaling; multiculturalism; communication".
- we are interested in typical soft skills an HR would look for
- infer skills based on what you read. For example a candidate that has experience as a consultant abroad must have good communication and summarization skills.

Candidate information:
{data}
"""

def extract_years_of_experience(candidate_json: dict)->int:
    start = min([xp["start_date"] for xp in candidate_json["experiences"]])
    ends = [xp["end_date"] for xp in candidate_json["experiences"]]
    if "" in ends:
        end = datetime.now().strftime("%Y-%m-%d")
    else:
        end = max(ends)

    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    diff_years = (end_date - start_date).days / 365
    years_of_experience = int(diff_years) if diff_years.is_integer() else int(diff_years) + 1
    return years_of_experience

def extract_highest_education(candidate_json: dict)->Literal["Bachelor", "Master", "PhD"]:
    return "Bachelor"
def extract_industry_sectors(candidate_json: dict)->str:
    return ""
def extract_skills(candidate_json: dict)->str:
    return ""
def extract_technologies(candidate_json: dict)->str:
    return ""

def grasp_candidate_info(candidate_json: dict)->QdrantInputCandidate:
    # TODO: ideally candidate should be a valid Pydantic model as defined in sata/models.py

    # Vector-like
    profile_summary = custom_generate_content(
        __PROFILE_SUMMARY_PROMPT.format(data=candidate_json)
    )
    industry_summary = custom_generate_content(
        __INDUSTRY_SUMMARY_PROMPT.format(data=candidate_json)
    )
    core_skills_summary = custom_generate_content(
        __CORE_TECHNICAL_SKILLS_SUMMARY_PROMPT.format(data=candidate_json)
    )
    core_soft_skills_summary = custom_generate_content(
        __CORE_SOFT_SKILLS_SUMMARY_PROMPT.format(data=candidate_json)
    )

    # precisse_extracts
    years_of_experience = extract_years_of_experience(candidate_json)
    highest_education = extract_highest_education(candidate_json)
    industry_sectors = extract_industry_sectors(candidate_json)
    skills = extract_skills(candidate_json)
    tehnologies_used = extract_technologies(candidate_json)

    qdrantInputCandidate = QdrantInputCandidate(
        first_name=candidate_json["first_name"],
        last_name=candidate_json["last_name"],
        profile_summary=profile_summary,
        industry_summary=industry_summary,
        core_skills_summary=core_skills_summary,
        core_soft_skills_summary=core_soft_skills_summary,
        years_of_experience=years_of_experience,
        highest_education=highest_education,
        industry_sectors=industry_sectors,
        skills=skills,
        tehnologies_used=tehnologies_used
    )

    return qdrantInputCandidate
