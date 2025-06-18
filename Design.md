# Design

Design documentation for the [task](Task.md) at hand

## App logic

- We are building an API that can access a job request, and a candidate database
- We have to design the job matching in such a way that core skills are job-agnostic and could work for absolutely everything
- The job requirements should somehow match the extracted skills of a candidate
- Candidates should be assigned a matching score and ranked based on it. Ideally this process should be explicit for traceability and evolutivity.

Challenges:

- ideally the extraction of skills from a candidate should be done whilst having in mind the exact job description. Take the example of a job in a specific sector like "cybersecurity". If the extraction just says "software" it would be too vague. However this approach clearly is not compatible with production as it would need a full scan of the database on every query. Consequently it would be best to precharge the extraction. So that at match-time, only an efficient operation is done.
  
## Diving into logic details

Using AI, I reached the following conclusion regarding a potential grid to extract from candidates and job descriptions alike

Candidate -> db extraction (Non-relational ideally for column evolutivity)

```json
{
    "years of experience":"<int>",
    "highest education":"<bach/mast/phd>",
    "top X% worldwide":"< x< 50%, 50% <= x < 10%, 10% <= x < 1%, 1% <= x < 0.1%, x >= 0.1% >",
    "industry_sectors":"<list as exhaustive as can be based on company names and job desc: >",
    "core skills":"list of key skills used",
    "technology used":"list of technologies used",
    "languages spoken": "list of languages spoken",
}
```

Candidate -> vector extraction

```json
{
    "profile summary":"a detailed profile summary",
    "industry_summary":"a detailed summary of the past industries the candidate worked in",
    "core technical skills":"list of core know-how used",
    "core soft skills":"list of core soft skills used",
}
```

Now of course when matching with a job, we cannot afford to compare text for every candidate with the job description... Which means we must find a way to transform this matching into an efficient operation. Most likely vector-comparison.

Challenges:

- listing the sectors exhaustively can be difficult. A good prompt must be used. Cybersecurity should lead to "engineering, software, cybersecurity" for exemple. In real-life, using the existing database to define all categories, reviewed by a human could make a lot of sense. Then we could specifically fine-tune a text classifier for this specific purpose.
- similarly for the core skills used: a specific software library should imply its corresponding programming language, a specific skill like "M&A" should imply financial analysis, etc. Defining those is no small task.
- list of languages should be standardized (for exp chinese should only be Mandarin, Cantonese. Quebecois should be French, etc.)
- some elements of the search are more of a pre-filter than an actual match. Here are some examples:
  - years of experience
  - languages included
  - key technologies mentioned
- some elements are more of a similarity search
  - sectors
  - core skills
  - technical skills

Consequently any job candidate should lead to

1. a list of filters for the db given a template query. Thsi should determine the candidated reviewed for the job search
2. some descriptions for the sector, core and technical skills that are text converted to vectors for matching in the filtered list.

Something we will not do in the context of this task, but that should definitely be done in production: building a tree-like graph of all possible sectors and skills periodically. For example engineering -> software -> AI -> agents.
I believe from personal experience that actual technologies should be distinct from core skills. For example you can do AI with Python or C or TS and you could use Pytorch or Tensorflow or something else. The how and the what are 2 distinct things.

Also the generation of these jsons should probably be done in various steps following a clear workflow to maximize prompt precision and result standardization. We will here lower the number of prompts to a minimum for the sake of this POC

## Architecture

- Backend: FastAPI - to accept the job matching request
- LLM: Gemini - in its free version (for e to try here) it is very convenient (and accepts documents as input if need be)
- embedding: for the sake of the POC, I may use HF's [sentence-tranceformers](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), or something I would use in production say Gemini's [experimental embedding models](https://ai.google.dev/gemini-api/docs/embeddings) optimized for text similarity.
- database: Qdrant - ideally we need a scalable NO-SQL db + a vector db. Something that can both be used locally easily and also be deployed on the cloud. After research Qdrant is a technology that was designed precisely for this kind of hybrid search and seems very relevant.

These choices are in theory good for testing locally, but also very scalable.
I would probably use fly.io + Qdrant hosted platform at first, then migrate everything to AWS as costs start to rise.

## Evaluation

Intermediary (almost unit tests)

Final test

- For a given job and list of candidates, check that I get the top candidate

Since this is a POC and I care more about showing the architecture than the actual result, tests will be extremely light on this repo.

## Chronology

- [x] generate 100 synthetic profile with a dedicated data/ candidate_generation.py which has a main func. Make that a click app
- [ ] under src/embed define functions to embed candidate profiles using Qdrant with appropriate subfunctions.
- [ ] under src/query define functions to query the database given a job description. It may involve editing src/embed to embed/adapt the job desc as well
- [ ] create the fastapi endpoints with proper CRUD validation
