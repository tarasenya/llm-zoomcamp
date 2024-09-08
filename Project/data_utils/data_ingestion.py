import json
from pathlib import Path 
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm
import hashlib
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import text_retrieval_metrics

load_dotenv(find_dotenv())

client = OpenAI()

es_client = Elasticsearch(['http://localhost:9200'])
es_client.info()

model_name = 'multi-qa-MiniLM-L6-cos-v1'
model = SentenceTransformer(model_name)



with open(Path().cwd().parents[0]/'data'/'initial_data.json', 'r') as f:
    data = json.load(f)


for doc in data:
    doc['vague_embedding'] = model.encode(doc['vague']).tolist()
    concatenated_fields = doc['vague'] + doc['actual']
    doc['id'] = hashlib.md5(concatenated_fields.encode()).hexdigest()


with open(Path().cwd().parents[0]/'data'/'initial_data_w_id.json', 'w') as f:
    json.dump(data, f)



index_settings = {
    'settings': {
        'number_of_shards': 1,
        'number_of_replicas': 0
    },  
    'mappings': {
        'properties': {
            'id': {'type': 'keyword'},
            'vague': {'type': 'text'},
            'actual': {'type': 'text'},
            'vague_embedding': {'type': 'dense_vector', 
                                'dims': 384,
                                'index': True,
                                'similarity': 'cosine'}
        }
    }
}


index_name = 'vague-actual'
es_client.indices.delete(index=index_name, ignore_unavailable=True)
es_client.indices.create(index=index_name, body=index_settings)


for doc in tqdm(data):
    es_client.index(index=index_name, id=doc['id'], body=doc)


def elastic_search_knn(vector):
    knn = {
        'field': 'vague_embedding',
        'query_vector': vector,
        'num_candidates': 100,
        'k':5
    }
    search_query = {'knn': knn,
                    '_source': ['vague', 'actual', 'id']
                    }
    es_results = es_client.search(index=index_name, body=search_query)
    
    result_docs = []
    for hit in es_results['hits']['hits']:
        result_docs.append(hit['_source'])
    
    return result_docs    


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


def rag(vague, gpt_model='gpt-4o-mini'):
    vectorized_vague= model.encode(vague)
    search_results = elastic_search_knn(vectorized_vague)
    prompt = build_prompt(vague, search_results=search_results)
    answer = llm(prompt, gpt_model=gpt_model)
    return answer


df_ground_truth = pd.read_csv('../data/ground_truth_data.csv')



ground_truth = df_ground_truth.to_dict(orient='records')
import text_retrieval_metrics


# In[23]:


relevance_total = []
for entry in tqdm(ground_truth):
    doc_id = entry['doc_id']
    results = elastic_search_knn(vector=model.encode(entry['vague']))
    relevance = [document['id'] == doc_id for document in results]
    relevance_total.append(relevance)


# In[29]:


text_retrieval_metrics.hit_rate(relevance_total)


# In[30]:


text_retrieval_metrics.mrr(relevance_total)


# In[ ]:




