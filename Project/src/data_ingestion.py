import json
from pathlib import Path
from elasticsearch import AsyncElasticsearch
from sentence_transformers import SentenceTransformer
import hashlib
import asyncio
from tqdm.asyncio import tqdm
from loguru import logger
from typing import List, Dict, Any
from abc import ABC, abstractmethod

class AbstractElasticsearchIngestion(ABC):
    def __init__(self, es_host: str, index_name: str, model_name: str,
                 dims: int=None):
        self.es_client = AsyncElasticsearch([es_host])
        self.index_name = index_name
        if model_name is not None:
            self.model = SentenceTransformer(model_name)
        self.dims = dims    
        logger.add("elasticsearch_ingestion.log", rotation="10 MB")

    @abstractmethod
    async def load_and_process_data(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def create_index(self) -> None:
        pass

    async def index_document(self, doc: Dict[str, Any]) -> None:
        try:
            await self.es_client.index(index=self.index_name, id=doc['id'], body=doc)
        except Exception as e:
            logger.error(f"Error indexing document {doc['id']}: {str(e)}")

    async def run(self) -> None:
        logger.info("Starting Elasticsearch ingestion process")
        
        data: List[Dict[str, Any]] = await self.load_and_process_data()
        
        await self.create_index()
        
        logger.info("Starting document indexing")
        tasks: List[asyncio.Task] = [asyncio.create_task(self.index_document(doc)) for doc in data]
        await tqdm.gather(*tasks, desc="Indexing Progress")
        
        logger.info("Indexing process completed")
        await self.es_client.close()

class ElasticsearchIngestionForSemanticSearch(AbstractElasticsearchIngestion):
    async def load_and_process_data(self) -> List[Dict[str, Any]]:
        logger.info("Starting to load and process data")
        data_dir: Path = Path(__file__).resolve().parents[1]/'data'
        with open(data_dir/'initial_data.json', 'r') as f:
            data: List[Dict[str, Any]] = json.load(f)
        data_w_id: List[Dict[str, Any]] = []
        for doc in tqdm(data, desc="Processing documents"):
            doc['vague_embedding'] = self.model.encode(doc['vague']).tolist()
            concatenated_fields: str = doc['vague'] + doc['actual']
            doc['id'] = hashlib.md5(concatenated_fields.encode()).hexdigest()
            data_w_id.append(doc)
        
        with open(data_dir/'initial_data_w_id.json', 'w') as f:
            json.dump(data_w_id, f)
        
        logger.info(f"Processed {len(data)} documents")
        return data_w_id

    async def create_index(self) -> None:
        logger.info(f"Creating index: {self.index_name}")
        index_settings: Dict[str, Any] = {
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
                                        'dims': self.dims,
                                        'index': True,
                                        'similarity': 'cosine'}
                }
            }
        }
        
        await self.es_client.indices.delete(index=self.index_name, ignore=[404])
        await self.es_client.indices.create(index=self.index_name, body=index_settings)
        logger.info(f"Index {self.index_name} created successfully")


class ElasticSearchIngestionForKeywordSearch(AbstractElasticsearchIngestion):
    
    async def load_and_process_data(self) -> List[Dict[str, Any]]:
        logger.info("Starting to load and process data")
        data_dir: Path = Path(__file__).resolve().parents[1]/'data'
    
        with open(data_dir/'initial_data.json', 'r') as f:
            data: List[Dict[str, Any]] = json.load(f)
    
        data_w_id: List[Dict[str, Any]] = []
        for doc in tqdm(data, desc="Processing documents"):
            concatenated_fields: str = doc['vague'] + doc['actual']
            doc['id'] = hashlib.md5(concatenated_fields.encode()).hexdigest()
            data_w_id.append(doc)
        
        with open(data_dir/'initial_data_w_id_keyword.json', 'w') as f:
            json.dump(data_w_id, f)
        
        logger.info(f"Processed {len(data)} documents")
        return data_w_id
    
    async def create_index(self) -> None:
        logger.info(f"Creating index: {self.index_name}")
        index_settings: Dict[str, Any] = {
       "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
                    },
        "mappings": {
            "properties": {
                "vague": {"type": "text"},
                "actual": {"type": "text"},
                          }
                    }
                                         }
        
        await self.es_client.indices.delete(index=self.index_name, ignore=[404])
        await self.es_client.indices.create(index=self.index_name, body=index_settings)
        logger.info(f"Index {self.index_name} created successfully")
        
async def main_semantic_search(model_name='multi-qa-MiniLM-L6-cos-v1',
                               index_name='vague-actual',
                               dims=384,
                               es_host='http://localhost:9200'):
    ingestion = ElasticsearchIngestionForSemanticSearch(
        es_host=es_host,
        index_name=index_name,
        model_name=model_name,
        dims=dims
    )
    await ingestion.run()

async def main_keyword_search():
    ingestion = ElasticSearchIngestionForKeywordSearch(
        es_host='http://localhost:9200',
        index_name='vague_actual_keyword',
        model_name=None
    )
    await ingestion.run()    
class ElasticsearchIngestionForHybridSearch(AbstractElasticsearchIngestion):
    def __init__(self, es_host: str, index_name: str, model_name: str, dims: int):
        super().__init__(es_host, index_name, model_name, dims)

    async def load_and_process_data(self) -> List[Dict[str, Any]]:
        logger.info("Starting to load and process data for hybrid search")
        data_dir: Path = Path(__file__).resolve().parents[1]/'data'
        
        with open(data_dir/'initial_data.json', 'r') as f:
            data: List[Dict[str, Any]] = json.load(f)
        
        data_w_id: List[Dict[str, Any]] = []
        for doc in tqdm(data, desc="Processing documents for hybrid search"):
            # Generate embedding for semantic search
            doc['vague_embedding'] = self.model.encode(doc['vague']).tolist()
            
            # Create a combined field for better keyword matching
            doc['combined_text'] = f"{doc['vague']} {doc['actual']}"
            
            # Generate a unique ID
            concatenated_fields: str = doc['vague'] + doc['actual']
            doc['id'] = hashlib.md5(concatenated_fields.encode()).hexdigest()
            
            data_w_id.append(doc)
        
        with open(data_dir/'initial_data_w_id_hybrid.json', 'w') as f:
            json.dump(data_w_id, f)
        
        logger.info(f"Processed {len(data)} documents for hybrid search")
        return data_w_id

    async def create_index(self) -> None:
        logger.info(f"Creating hybrid search index: {self.index_name}")
        index_settings: Dict[str, Any] = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "custom_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop", "snowball"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "vague": {
                        "type": "text",
                        "analyzer": "custom_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "actual": {
                        "type": "text",
                        "analyzer": "custom_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "combined_text": {
                        "type": "text",
                        "analyzer": "custom_analyzer"
                    },
                    "vague_embedding": {
                        "type": "dense_vector",
                        "dims": self.dims,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
        }
        
        await self.es_client.indices.delete(index=self.index_name, ignore=[404])
        await self.es_client.indices.create(index=self.index_name, body=index_settings)
        logger.info(f"Hybrid search index {self.index_name} created successfully")

async def main_hybrid_search(model_name='all-mpnet-base-v2',
                             index_name='vague-actual-hybrid',
                             dims=768,
                             es_host='http://localhost:9200'):
    ingestion = ElasticsearchIngestionForHybridSearch(
        es_host=es_host,
        index_name=index_name,
        model_name=model_name,
        dims=dims
    )
    await ingestion.run()
    
if __name__ == "__main__":
    #asyncio.run(main_semantic_search(model_name='all-mpnet-base-v2',
    #                                 index_name='vague-actual-mpnet',
    #                                dims=768))
    #asyncio.run(main_key_work_search())
    asyncio.run(main_hybrid_search())