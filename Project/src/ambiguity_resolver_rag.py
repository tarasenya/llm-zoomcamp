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


def create_rag(elastic_url=None):
    if elastic_url:
        os.environ['ELASTIC_URL'] = elastic_url
    
    elastic_semantic_searcher = elastic_search_engine.ElasticSemanticSearcher(
        index_name="vague-actual-mpnet",
        elastic_search_client_uri=os.getenv("ELASTIC_URL", "http://localhost:9200"),
    )

    print(f'ELASTIC_URL {os.getenv("ELASTIC_URL")}')
    # defining new RAG with a prompt above
    return rag.ChatGPTRAG(
        elastic_searcher=elastic_semantic_searcher,
        prompt_template=ambiguity_resolver_prompt,
        llm_model="gpt-4o-mini",
        sentence_transformer_name="all-mpnet-base-v2",
    )

# Initialize with default settings
ambiguity_resolver_rag = create_rag()