from qdrant_client import QdrantClient, models 
from config import _ROOT_PATH
from data.models import JobMatchingCriteria, QdrantPointCandidate 
from qdrant_client.http.models import PointStruct, ScoredPoint
from qdrant_client.http.models import Filter, FieldCondition, Range, MatchText

# TODO: switch to dev mode with a docker local URL call then cloud
QDRANT_CLIENT = QdrantClient(path=(_ROOT_PATH / "qdrant.db").as_posix())
QDRANT_CANDIDATE_COLLECTION_NAME = "candidates"
QDRANT_EMBEDDING_MODEL_NAME = "models/text-embedding-004"
EMBEDDING_SIZE = 768


def init():
    # creates the collection of candidates if it does not exist
    #loads it otherwise
    if not QDRANT_CLIENT.collection_exists(QDRANT_CANDIDATE_COLLECTION_NAME):
        QDRANT_CLIENT.create_collection(
            QDRANT_CANDIDATE_COLLECTION_NAME,
            vectors_config={
                "profile_summary": models.VectorParams(size=768, distance=models.Distance.COSINE),
                "industry_summary": models.VectorParams(size=384, distance=models.Distance.DOT),
                "core_skills_summary": models.VectorParams(size=128, distance=models.Distance.COSINE),
                "core_soft_skills_summary": models.VectorParams(size=128, distance=models.Distance.COSINE)
            }
        )

def add_candidate(candidate:QdrantPointCandidate)->None:
    # adds a candidate to the collection
    # add an id on the fly

    #TODO: keep track of ids with a proper counter in a QDRANT-friendly way
    points, _ = QDRANT_CLIENT.scroll(
        collection_name=QDRANT_CANDIDATE_COLLECTION_NAME,
        limit=1,
        with_payload=False,
        with_vectors=False,
        order_by=[("id", "desc")]
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

def job_matching(job:JobMatchingCriteria)->list[ScoredPoint]:
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
    hits = QDRANT_CLIENT.search(
        collection_name=QDRANT_CANDIDATE_COLLECTION_NAME,
        query_vector=job.job_summary,
        vector_name="profile_summary",
        limit=10,  # large enough to get good overlaps
        with_payload=True,
        query_filter=query_filter
    )
    return hits