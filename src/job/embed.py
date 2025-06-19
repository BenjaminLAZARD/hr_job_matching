from data.models import JobMatchingCriteria
from src.embed import EDUCATION_MAP, embed_text


def embed_job(job: dict) -> JobMatchingCriteria:
    min_education = None
    min_education = EDUCATION_MAP.get(job.get("required_education", ""), None)

    min_xp_years = 0
    max_xp_years = 100

    mandatory_industry_sector = ""

    summary = f"{job['job_title']}: {job['job_description']}"
    job_summary = embed_text(summary)

    return JobMatchingCriteria(
        min_xp_years=min_xp_years,
        max_xp_years=max_xp_years,
        min_education=min_education,
        mandatory_industry_sector=mandatory_industry_sector,
        job_summary=job_summary
    )