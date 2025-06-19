import json
from pathlib import Path
from qdrant_client import QdrantClient, models 
from src.candidate.embed import embed_candidate, grasp_candidate_info
from config import _ROOT_PATH
from data.models import JobMatchingCriteria, QdrantPointCandidate 
from qdrant_client.http.models import PointStruct, ScoredPoint
from qdrant_client.http.models import Filter, FieldCondition, Range
from data.models import CandidatePayload
# from pathlib import Path
# from src.candidate.embed import embed_candidate

# TODO: switch to dev mode with a docker local URL call then cloud
QDRANT_CLIENT = QdrantClient(path=(_ROOT_PATH / "qdrant.db").as_posix())
QDRANT_CANDIDATE_COLLECTION_NAME = "candidates"


def get_qdrant_client():
    """
    Returns a Qdrant client instance.
    This can be used to interact with the Qdrant database.
    """
    # TODO: adapt depnding on the environment (local, dev, prod)
    # In Prod this should be a client connecting over http
    return QDRANT_CLIENT


def init():
    # creates the collection of candidates if it does not exist
    #loads it otherwise
    if not QDRANT_CLIENT.collection_exists(QDRANT_CANDIDATE_COLLECTION_NAME):
        QDRANT_CLIENT.create_collection(
            QDRANT_CANDIDATE_COLLECTION_NAME,
            vectors_config={
                "profile_summary": models.VectorParams(size=768, distance=models.Distance.COSINE),
                "industry_summary": models.VectorParams(size=768, distance=models.Distance.DOT),
                "core_skills_summary": models.VectorParams(size=768, distance=models.Distance.COSINE),
                "core_soft_skills_summary": models.VectorParams(size=768, distance=models.Distance.COSINE)
            }
        )

    #TODO: improve this: make it conditional to an env variable (local, dev, prod)
    #TODO: consider using FASTPI's lifespan function
    data_dir = _ROOT_PATH / "data" / "generated"
    for json_file in Path(data_dir).glob("*.json"):
        candidate_dict = json.loads(json_file.read_text())
        candidate_payload = CandidatePayload(**candidate_dict)
        candidateInput = grasp_candidate_info(candidate_payload)
        candidatePoint = embed_candidate(candidateInput)
        add_candidate(candidatePoint, QDRANT_CLIENT)
        print(f"Added candidate from {json_file.name} to Qdrant collection {QDRANT_CANDIDATE_COLLECTION_NAME}")

def add_candidate(candidate:QdrantPointCandidate, qdrant_client:QdrantClient)->None:
    # adds a candidate to the collection
    # add an id on the fly

    #TODO: keep track of ids with a proper counter in a QDRANT-friendly way
    points, _ = qdrant_client.scroll(
        collection_name=QDRANT_CANDIDATE_COLLECTION_NAME,
        limit=1,
        with_payload=False,
        with_vectors=False,
        order_by=models.OrderBy(
            key="id",
            direction=models.Direction.DESC,  # default is "asc"
            start_from=0,  # start from this value
        )
    )
    if points:
        next_id = int(points[0].id) + 1
    else:
        next_id = 0
    
    point = PointStruct(
        id=next_id,  
        payload=candidate.payload.model_dump(),
        vector=candidate.vectors.model_dump()
    )
    QDRANT_CLIENT.upsert(collection_name=QDRANT_CANDIDATE_COLLECTION_NAME, points=[point])


def remove_candidate():
    # by id
    ...

def modify_candidate():
    # by id
    ...

def job_matching(job:JobMatchingCriteria, qdrant_client:QdrantClient)->list[ScoredPoint]:
    if job.min_xp_years is None:
        minxp = 0
    else:
        minxp = job.min_xp_years
    if job.max_xp_years is None:
        maxp = 100
    else:
        maxp = job.max_xp_years

    meduc = 0 if job.min_education is None else job.min_education
    
    #TODO: add filters for everything(industry or key technologies)
    query_filter = Filter(
        must=[
            FieldCondition(
                key="years_of_experience",
                range=Range(gte=minxp, lte=maxp)
            ),
            FieldCondition(
                key="highest_education",
                range=Range(gte=meduc)
            )
        ]
    )

    # similarity search
    #TODO: perform weighted average or reciprocal rank fusion with all available vectors and several similarity searches
    hits = qdrant_client.search(
        collection_name=QDRANT_CANDIDATE_COLLECTION_NAME,
        query_vector=job.job_summary,
        vector_name="profile_summary",
        limit=10,  # large enough to get good overlaps
        with_payload=True,
        query_filter=query_filter
    )
    return hits