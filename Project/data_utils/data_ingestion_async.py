import json
from pathlib import Path
from elasticsearch import AsyncElasticsearch
from sentence_transformers import SentenceTransformer
import hashlib
import asyncio
from tqdm.asyncio import tqdm
from loguru import logger

# Initialize AsyncElasticsearch client
es_client = AsyncElasticsearch(['http://localhost:9200'])

# Initialize SentenceTransformer model
model_name = 'multi-qa-MiniLM-L6-cos-v1'
model = SentenceTransformer(model_name)

# Configure loguru logger
logger.add("elasticsearch_ingestion.log", rotation="10 MB")

async def load_and_process_data():
    logger.info("Starting to load and process data")
    data_dir = Path(__file__).resolve().parents[1]/'data'
    with open(data_dir/'initial_data.json', 'r') as f:
        data = json.load(f)
    data_w_id = []
    for doc in tqdm(data, desc="Processing documents"):
        doc['vague_embedding'] = model.encode(doc['vague']).tolist()
        concatenated_fields = doc['vague'] + doc['actual']
        doc['id'] = hashlib.md5(concatenated_fields.encode()).hexdigest()
        data_w_id.append(doc)
    
    with open(data_dir/'initial_data_w_id.json', 'w') as f:
        json.dump(data_w_id, f)
    
    logger.info(f"Processed {len(data)} documents")
    return data

async def create_index(index_name):
    logger.info(f"Creating index: {index_name}")
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
    
    await es_client.indices.delete(index=index_name, ignore=[404])
    await es_client.indices.create(index=index_name, body=index_settings)
    logger.info(f"Index {index_name} created successfully")

async def index_document(index_name, doc):
    try:
        await es_client.index(index=index_name, id=doc['id'], body=doc)
    except Exception as e:
        logger.error(f"Error indexing document {doc['id']}: {str(e)}")

async def main():
    index_name = 'vague-actual'
    
    logger.info("Starting Elasticsearch ingestion process")
    
    data = await load_and_process_data()
    
    await create_index(index_name)
    
    logger.info("Starting document indexing")
    tasks = [index_document(index_name, doc) for doc in data]
    await tqdm.gather(*tasks, desc="Indexing Progress")
    
    logger.info("Indexing process completed")
    await es_client.close()

if __name__ == "__main__":
    asyncio.run(main())