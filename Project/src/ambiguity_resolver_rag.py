from src import rag, elastic_search_engine

ambiguity_resolver_prompt = """You are an Ambiguity Resolver for tech management communication. Your task is to:

1. Interpret the VAGUE STATEMENT from an IT manager
2. Consider the given CONTEXT
3. Rewrite the statement in clear, specific, and actionable terms

Provide only the rewritten statement without additional commentary.

VAGUE STATEMENT: {vague}

CONTEXT: {context}

CLEAR STATEMENT:""".strip()

elastic_semantic_searcher = elastic_search_engine.ElasticSemanticSearcher(index_name='vague-actual-mpnet')

# defining new RAG with a prompt above
ambiguity_resolver_rag= rag.ChatGPTRAG(elastic_searcher=elastic_semantic_searcher,
                 prompt_template=ambiguity_resolver_prompt, 
                 llm_model='gpt-4o-mini',
                 sentence_transformer_name='all-mpnet-base-v2')