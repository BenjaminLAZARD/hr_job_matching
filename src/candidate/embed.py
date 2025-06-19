from datetime import datetime
from typing import Literal
from data.models import QdrantInputCandidate, QdrantPointCandidate, QdrantPointCandidatePayload, QdrantPointCandidateVectors
from src.embed import EDUCATION_MAP, custom_generate_content, embed_text
from data.models import CandidatePayload

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
- extrapolate based on information you have on the companies and resume of the candidate. for example if the candidate is a full-stack engineer, you can automatically deduce that he works in the software industry as well. if he worked in a young startup in the realm of construction works and handles data-engineering, then you can add "construction, startup, building, data, software" for exp. Try to be exhaustive. 
- Do not mention the names of the companies, just the industries
- provide a summary of up to 10 lines

Candidate information:
{data}
"""
__CORE_TECHNICAL_SKILLS_SUMMARY_PROMPT = """You are a helpful Human Resource Assistance. Your task is to provide a summary of the core technical skills the candidate has.

Bear in mind that you must
- We are interested in elements such as "software architecture; POCs; data-science; scaling" or "sales; growth-hacking; wine; no-code".
- we are not interested in the name of specific technologies. For exemple "python" is not a skill. high-level software programming is. "vue.js" is not a skill, but "frontend" is
- infer skills based on what you read. For example a candidate that has experience setting up FastApi automatically has experience with "backend, scaling, webapp"
- provide a summary of up to 10 lines.

Candidate information:
{data}
"""
__CORE_SOFT_SKILLS_SUMMARY_PROMPT = """You are a helpful Human Resource Assistance. Your task is to provide a summary of the core soft skills the candidate has.

Bear in mind that you must
- provide a list of items separated by semi-columns, initiated such as "management; scaling; multiculturalism; communication".
- we are interested in typical soft skills an HR would look for
- infer skills based on what you read. For example a candidate that has experience as a consultant abroad must have good communication and summarization skills.
- provide a summary of up to 10 lines.

Candidate information:
{data}
"""


def extract_years_of_experience(candidate_json: CandidatePayload) -> int:
    start = min([xp["start_date"] if xp["start_date"] is not None else "1900-01-01" for xp in candidate_json.experiences])
    ends = [xp["end_date"] if xp["end_date"] is not None else datetime.now().strftime("%Y-%m-%d") for xp in candidate_json.experiences]
    if "" in ends:
        end = datetime.now().strftime("%Y-%m-%d")
    else:
        end = max(ends) #type:ignore

    start_date = datetime.strptime(start, "%Y-%m-%d") #type:ignore
    end_date = datetime.strptime(end, "%Y-%m-%d")
    diff_years = (end_date - start_date).days / 365
    years_of_experience = (
        int(diff_years) if diff_years.is_integer() else int(diff_years) + 1
    )
    return years_of_experience


def extract_highest_education(
    candidate_json: CandidatePayload,
) -> Literal["Bachelor", "Master", "PhD", "None"]:
    educations = [ed["degree"] for ed in candidate_json.education]
    prompt = f"""Based on the following degrees, what is the highest education this person has? The answer must be a single word, either "Bachelor", "Master" or "PhD".
    {educations}
    """
    ed = custom_generate_content(prompt).strip()
    if "Bachelor" in ed:
        return "Bachelor"
    if "Master" in ed:
        return "Master"
    if "PhD" in ed:
        return "PhD"
    return "None"


def extract_industry_sectors(candidate_json: CandidatePayload) -> str:
    prompt = """You are a helpful Human Resource Assistance. Your task is to provide a summary of the industries the candidate worked in.

Bear in mind that you must
- provide a list of items separated by semi-columns, initiated such as "insurance; cars; actuary" or "cyber-security; software, start-up".
- extrapolate based on information you have on the companies and resume of the candidate. for example if the candidate is a full-stack engineer, you can automatically deduce that he works in the software industry as well. if he worked in a young startup in the realm of construction works and handles data-engineering, then you can add "construction, startup, building, data, software" for exp. Try to be exhaustive. 

- There could be up to 10 words

Candidate information:
{data}
    """
    out = custom_generate_content(prompt.format(data=candidate_json))
    return out


def extract_skills(candidate_json: CandidatePayload) -> str:
    prompt = """You are a helpful Human Resource Assistance. Your task is to provide a summary of the core technical skills the candidate has.

Bear in mind that you must
- provide a list of items separated by semi-columns, initiated such as "software architecture; POCs; data-science; scaling" or "sales; growth-hacking; wine; no-code".
- we are not interested in the name of specific technologies. For exemple "python" is not a skill. high-level software programming is. "vue.js" is not a skill, but "frontend" is
- infer skills based on what you read. For example a candidate that has experience setting up FastApi automatically has experience with "backend, scaling, webapp"

Candidate information:
{data}
"""
    out = custom_generate_content(prompt.format(data=candidate_json))
    return out


def extract_technologies(candidate_json: CandidatePayload) -> str:
    prompt = """You are a helpful Human Resource Assistance. Your task is to provide a list of specific tech skills the candidate has.

Bear in mind that you must
- provide a list of programinig languages, tools like word, photoshop, or other softwares, skills like "planing", "business-model", etc. being as specific as possible
- we are not interested in the name of core skills (like frontend, backend, architecture, etc.). We only want specific techs (vue.js, powerpoint, figma, etc.)
- infer skills based on what you read. For example a candidate that has experience setting up FastApi automatically has experience with "python"

Candidate information:
{data}
"""
    out = custom_generate_content(prompt.format(data=candidate_json))
    return out

def grasp_candidate_info(candidate_json: CandidatePayload) -> QdrantInputCandidate:
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
        first_name=candidate_json.first_name,
        last_name=candidate_json.last_name,
        profile_summary=profile_summary,
        industry_summary=industry_summary,
        core_skills_summary=core_skills_summary,
        core_soft_skills_summary=core_soft_skills_summary,
        years_of_experience=years_of_experience,
        highest_education=highest_education,
        industry_sectors=industry_sectors,
        skills=skills,
        tehnologies_used=tehnologies_used,
    )

    return qdrantInputCandidate

def embed_candidate(candidate: QdrantInputCandidate) -> QdrantPointCandidate:
    """
    Vectorizes the summaries
    """
    hed = EDUCATION_MAP.get(candidate.highest_education, 0)
    

    payload = QdrantPointCandidatePayload(
        first_name=candidate.first_name,
        last_name=candidate.last_name,
        years_of_experience=candidate.years_of_experience,
        highest_education=hed,
        industry_sectors=candidate.industry_sectors,
        skills=candidate.skills,
        tehnologies_used=candidate.tehnologies_used,
    )
    vectors = QdrantPointCandidateVectors(
        profile_summary = embed_text(candidate.profile_summary),
        industry_summary = embed_text(candidate.industry_summary), 
        core_skills_summary = embed_text(candidate.core_skills_summary),
        core_soft_skills_summary = embed_text(candidate.core_soft_skills_summary),
    )

    return QdrantPointCandidate(payload=payload, vectors=vectors)

# candidate_json = json.loads(Path("data/generated/Kwame_Boateng.json").read_text())

# extracted_candidate_info = grasp_candidate_info(candidate_json)
# qdrantPointCandidate = embed_candidate(extracted_candidate_info)
# print(extracted_candidate_info)