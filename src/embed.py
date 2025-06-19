from config import GOOGLE_CLIENT, MODEL_NAME
from google.genai import types


QDRANT_EMBEDDING_MODEL_NAME = "models/text-embedding-004"
EMBEDDING_SIZE = 768
EDUCATION_MAP = {"Bachelor": 1, "Master": 2, "PhD": 3}

def custom_generate_content(prompt: str) -> str:
    "wrapper around Google API"
    _model_config = types.GenerateContentConfig(temperature=1.0)
    response = GOOGLE_CLIENT.models.generate_content(
        model=MODEL_NAME,
        contents=[types.Part.from_text(text=prompt)],
        config=_model_config,
    ).text

    return response if response is not None else ""

def embed_text(text:str) -> list[float]:
    """
    Vectorizes the text using the Google Gemini API.
    Returns a list of floats representing the vector.
    """
    response = GOOGLE_CLIENT.models.embed_content(
        model=QDRANT_EMBEDDING_MODEL_NAME,
        contents=[text],
        config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY", output_dimensionality=EMBEDDING_SIZE)
    )
    embeddings = []
    if response.embeddings and response.embeddings[0].values is not None:
        embeddings = response.embeddings[0].values
    return embeddings


