from fastapi import FastAPI, Depends
from fastapi import status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from data.models import CandidatePayload, JobPayload
from src.db import add_candidate, job_matching, get_qdrant_client, init
from src.candidate.embed import embed_candidate, grasp_candidate_info
from src.job.embed import embed_job
import uvicorn

@asynccontextmanager
def lifespan(app: FastAPI):
    # Initialize Qdrant and collections at startup
    init()
    yield

app = FastAPI(lifespan=lifespan)

# TODO: make the API more RESTful, e.g. use /candidates and /jobs endpoints
# TOOD: define a proper CRUD models and separate models into other filess
# TODO: add the DB as a FASTAPI dependency injection pattern


@app.post("/candidate")
def db_add_candidate(candidate: CandidatePayload, qdrant=Depends(get_qdrant_client)):
    # Embed candidate and add to Qdrant
    candidateInput = grasp_candidate_info(candidate)
    candidatePoint = embed_candidate(candidateInput)
    add_candidate(candidatePoint, qdrant)
    return JSONResponse(
        content={"message": "Candidate added successfully"},
        status_code=status.HTTP_201_CREATED,
    )


@app.post("/jobs/search")
def job_similarity_search(payload: JobPayload, qdrant=Depends(get_qdrant_client)):
    # Embed job description and search similar jobs
    jobMatchingCriteria = embed_job(payload)
    results = job_matching(jobMatchingCriteria, qdrant)
    return JSONResponse(
        content={"results": results},
        status_code=status.HTTP_200_OK,
    )

if __name__ == "__main__":
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=8000, reload=True)
