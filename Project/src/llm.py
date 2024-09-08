from openai import OpenAI

client = OpenAI()

def build_prompt(query, search_results):
    prompt_template = """
    Your are a translator from vague boss language into an everyday language. Translate
    the VAGUE statement or question based on the CONTEXT. Provide a clear and concise answer.
    VAGUE: {vague}
    
    CONTEXT: {context}
    """.strip()
    
    context = ''
    for doc in search_results:
        context+= f"vague: {doc['vague']}\nactual: {doc['actual']}\n\n"
    prompt = prompt_template.format(vague=query, context=context)    
    return prompt

def llm(prompt, gpt_model='gpt-4o-mini'):
    response = client.chat.completions.create(model=gpt_model,
                                             messages=[{'role': 'user', 'content': prompt}],)
    return response.choices[0].message.content

def rag(vague, model, elastic_search_knn, gpt_model='gpt-4o-mini',):
    vectorized_vague= model.encode(vague)
    search_results = elastic_search_knn(vectorized_vague)
    prompt = build_prompt(vague, search_results=search_results)
    answer = llm(prompt, gpt_model=gpt_model)
    return answer