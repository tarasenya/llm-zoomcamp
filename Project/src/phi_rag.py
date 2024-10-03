"""
Implements a RAG that exploits Phi3 Model as an LLM model in Ollama fashion.
"""
import os

import elastic_search_engine
import rag


ambiguity_resolver_prompt = """You are an Ambiguity Resolver for tech management 
communication. Your task is to:

1. Interpret the VAGUE STATEMENT from an IT manager
2. Consider the given CONTEXT
3. Rewrite the statement in clear, specific, and actionable terms

Provide only the rewritten statement without additional commentary.

VAGUE STATEMENT: {vague}

CONTEXT: {context}

CLEAR STATEMENT:""".strip()


def create_ollama_rag(ollama_model_name: str, elastic_url=None):
    """
    Create an Ollama RAG instance with specified model and Elasticsearch configuration.
    :param ollama_model_name: Name of the Ollama model to use.
    :param elastic_url: Optional Elasticsearch URL, defaults to None.
    :return: Configured OllamaRag instance.
    """
    if elastic_url:
        os.environ['ELASTIC_URL'] = elastic_url
    
    elastic_semantic_searcher = elastic_search_engine.ElasticSemanticSearcher(
        index_name="vague-actual-mpnet",
        elastic_search_client_uri=os.getenv("ELASTIC_URL", "http://localhost:9200"),
    )

    print(f'ELASTIC_URL {os.getenv("ELASTIC_URL")}')
    # defining new RAG with a prompt above
    return rag.OllamaRag(
        elastic_searcher=elastic_semantic_searcher,
        prompt_template=ambiguity_resolver_prompt,
        llm_model=ollama_model_name,
        sentence_transformer_name="all-mpnet-base-v2",
    )

# Initialize with default settings
phi3_rag = create_ollama_rag('phi3')