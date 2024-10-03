"""
General functionality for LLM.
"""

from openai import OpenAI
from sentence_transformers import SentenceTransformer


client = OpenAI()


def build_prompt(query: str, search_results: list):
    """
    Based on search results and user query build a prompt to ChatGPT.
    """
    prompt_template = """
    Your are a translator from vague boss language into an everyday language. Translate
    the VAGUE statement or question based on the CONTEXT. 
    Provide a clear and concise answer.
    
    VAGUE: {vague}
    
    CONTEXT: {context}
    """.strip()

    context = ""
    for doc in search_results:
        context += f"vague: {doc['vague']}\nactual: {doc['actual']}\n\n"
    prompt = prompt_template.format(vague=query, context=context)
    return prompt


def llm(prompt, gpt_model="gpt-4o-mini") -> str:
    """
    Generate a response using a specified LLM.
    :param prompt: Input text for the LLM.
    :param gpt_model: Model to use, defaults to "gpt-4o-mini".
    :return: Generated response text.
    """
    response = client.chat.completions.create(
        model=gpt_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def rag(
    vague: str,
    model: SentenceTransformer,
    elastic_search_knn: dict,
    gpt_model="gpt-4o-mini",
):
    """
    Perform Retrieval-Augmented Generation (RAG).
    :param vague: Input query string.
    :param model: SentenceTransformer model for encoding.
    :param elastic_search_knn: Function for k-NN search in Elasticsearch.
    :param gpt_model: LLM model to use, defaults to "gpt-4o-mini".
    :return: Generated answer based on retrieved context.
    """
    vectorized_vague = model.encode(vague)
    search_results = elastic_search_knn(vectorized_vague)
    prompt = build_prompt(vague, search_results=search_results)
    answer = llm(prompt, gpt_model=gpt_model)
    return answer
