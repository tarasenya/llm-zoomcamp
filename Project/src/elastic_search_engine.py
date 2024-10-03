"""
Includes ElasticSearch functionality for different cases.
"""
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


class ElasticSearcher:
    def __init__(
        self, index_name: str, elastic_search_client_uri="http://localhost:9200"
    ):
        self.client = Elasticsearch([elastic_search_client_uri])
        self.index_name = index_name

    def search_query(self, input_argument):
        raise NotImplementedError

    def search(self, input_argument):
        es_results = self.client.search(
            index=self.index_name, body=self.search_query(input_argument)
        )

        result_docs = []
        for hit in es_results["hits"]["hits"]:
            result_docs.append(hit["_source"])

        return result_docs


class ElasticKeywordSearcher(ElasticSearcher):
    def search_query(self, input_argument):
        _search_query = {
            "size": 5,
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": input_argument,
                            "fields": ["vague^3", "actual"],
                            "type": "best_fields",
                        }
                    },
                }
            },
        }
        return _search_query


class ElasticSemanticSearcher(ElasticSearcher):
    def search_query(self, input_argument):
        knn = {
            "field": "vague_embedding",
            "query_vector": input_argument,
            "num_candidates": 100,
            "k": 5,
        }
        _search_query = {"knn": knn, "_source": ["vague", "actual", "id"]}
        return _search_query


class ElasticHybridSearcher(ElasticSearcher):
    def __init__(
        self,
        index_name: str,
        elastic_search_client_uri="http://localhost:9200",
        model_name="all-mpnet-base-v2",
    ):
        super().__init__(index_name, elastic_search_client_uri)
        self.model = SentenceTransformer(model_name)

    def search_query(self, input_argument):
        # Generate embedding for the input query
        query_vector = self.model.encode(input_argument).tolist()

        search_query = {
            "size": 10,
            "query": {
                "script_score": {
                    "query": {
                        "bool": {
                            "should": [
                                {
                                    "multi_match": {
                                        "query": input_argument,
                                        "fields": [
                                            "vague^3",
                                            "vague.keyword^2",
                                            "actual^2",
                                            "actual.keyword",
                                            "combined_text^4",
                                        ],
                                        "type": "best_fields",
                                        "fuzziness": "AUTO",
                                    }
                                }
                            ]
                        }
                    },
                    "script": {
                        "source": "(cosineSimilarity(params.query_vector, \
                            'vague_embedding') + 1.0) * 0.5 + _score * 0.5",
                        "params": {"query_vector": query_vector},
                    },
                }
            },
            "_source": ["vague", "actual", "id"],
        }

        return search_query
