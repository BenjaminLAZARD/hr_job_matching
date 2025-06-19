from pathlib import Path
import json
from config import GOOGLE_CLIENT, MODEL_NAME
from google import genai
from google.genai import types
from alive_progress import alive_bar  # type: ignore
from time import sleep


def generate_candidates(
    n: int,
    client: genai.Client = GOOGLE_CLIENT,
    model_name: str = MODEL_NAME,
    example_json: Path = Path("data/samples/candidate.json"),
    backup_dir: Path = Path("data/generated"),
) -> None:
    """
    Generates n candidates based on the provided json.
    This function generates extracts directly from resumes
    """
    _model_config = types.GenerateContentConfig(temperature=1.2)
    backup_dir.mkdir(exist_ok=True, parents=True)
    # TODO: use pydantic validation
    pattern = json.loads(example_json.read_text())

    prompt = """
You are a synthetic data generator.
Your task is to generate a valid json extraction from a candidate resume for use in a database
Generate a random json following the provided pattern.
The output must respect these conditions:
- be a valid json
- use double quotes only not single quotes for the json (and escape properly strings if need be)
- have the same fields than the example (the number of profesisonal experiences or educations can change)
- be realistic with a random name, detailed experiences, etc.
- possible profiles are product, sales, backend, frontend, data engineer, fullstack, architect, etc.

pattern to follow: 
{pattern}

sample story:
{story}

Your output:
"""
    with alive_bar(n, title="Generating candidates") as bar:
        for i in range(n):
            story = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_text(
                        text="You are a synthetic data generator. Give me a random first name and last name for an employee, pick his job (possible profiles are product, sales, finance, etc.), describe in 3 lines what he/she does. Provide his/her country, name of colleges attended, and name of companies. Use random companies names (realistic, big or small). Make the name ethnically diverse, use all possible countries including Europe (France, Spain, Greece, Italy, Poland, Estonia). Do not use names Anya, Elias, Lakshmi, Maya, Kwame, Jian, Javier, Eliza, Aisha"
                    )
                ],
                config=_model_config,
            ).text
            print(story)

            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_text(
                        text=prompt.format(story=story, pattern=pattern)
                    )
                ],
                config=_model_config,
            )

            if response and response.text is not None:
                cleaned_response = (
                    response.text.replace("```json", "").replace("```", "").strip()
                )
                try:
                    candidate_dict = json.loads(cleaned_response)
                    candidate_json = json.dumps(
                        candidate_dict, ensure_ascii=False, indent=4
                    )
                    file_name = (
                        backup_dir
                        / f"{candidate_dict["first_name"]}_{candidate_dict["last_name"]}.json"
                    )
                    file_name.write_text(candidate_json, encoding="utf-8")
                except json.decoder.JSONDecodeError as e:
                    # TODO: use proper login
                    print(f"error processing {cleaned_response}, {e}")
                    continue
            bar()
            if i%5:
                sleep(5)


generate_candidates(100)
