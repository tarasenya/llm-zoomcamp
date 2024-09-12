# LLM final Project

## Brief description of the project

Everyday one confronts with vague statements of his/her boss. Often a boss tries to formulate tasks, give pieces of advice indirect, which causes lots of misunderstanding. Experiencing this from time to time I considered it to be a good idea to build a RAG, which helps an IT employee to understand what a boss really wants. Hence an aim of this project is:
- to build a RAG system that gets a vague question/statement from a boss and 'translates' it into the form one can unambiguously understand.
- build a UI for this RAG system
- Containerize it and deploy to a GCP

## Data Generation
Since it is a sensible topic, the corresponding data has been generated using ChatGPT.
This is done using ```src/inital_data_generation.py```. The corresponding output has been saved to ```data/initial_data.json```.

## Ground Truth Generation
Ground truth has been also generated using ChtaGPT (_gpt-4o-mini_ model). The result has been saved to ```data/ground_truth_data.csv```. This data has been used for a retrieval evaluation.

## Data Retrieval
Data Retrieval has been evaluated using __hit_rate__ and __mrr__ metrics. I refer to the [Evaluation retrieval notebook](./notebooks/retrieval_evaluation.ipynb).
The following retrieval possibilities has been considered:
 - Semantic search exploiting ```SentenceTransformer``` with the model _multi-qa-MiniLM-L6-cos-v1_.
 - Semantic search exploiting ```SentenceTransformer``` with the model _all-mpnet-base-v2_.
 - Keyword search.
  For every retrieval evaluation a separate index has been defined (see [ingestion code](./src/data_ingestion.py)) and a separate class for a search functionality has been introduced (see [elastic search code](./src/elastic_search_engine.py)). The results are as the following:

  | Metric   | keyword search | multi-qa-MiniLM-L6-cos-v1 | all-mpnet-base-v2 |
  |----------|----------------|---------------------------|-------------------|
  | hit_rate | 0.95           | 0.87                      | 0.97              |
  | mrr      | 0.90           | 0.81                      | 0.93              |
 
 I will use a knn elastic search with __all-mpnet-base-v2__ module in the future.

Disclaimer: The results are so good, since the data has been generated using ChatGPT,hence we do not have the variability of the real world. Of course, one can play with prompts to achieve it, but due to lack of time I leave it as it is.
## RAG

### RAG Evaluation