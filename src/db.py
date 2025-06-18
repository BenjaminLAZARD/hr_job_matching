from qdrant_client import QdrantClient, models 
from config import _ROOT_PATH 


# TODO: switch to dev mode with a docker local URL call then cloud
QDRANT_CLIENT = QdrantClient(path=(_ROOT_PATH / "qdrant.db").as_posix())
QDRANT_EMBEDDING_MODEL_NAME = "models/text-embedding-004"
