from elasticsearch import Elasticsearch

class ElasticSearcher:
    def __init__(self, index_name: str, elastic_search_client_uri='http://localhost:9200'):
        self.client = Elasticsearch([elastic_search_client_uri])
        self.index_name = index_name
    
    def search_query(self, input_argument):
        raise NotImplementedError
        
    def search(self, input_argument):
        es_results = self.client.search(index=self.index_name, 
                                    body=self.search_query(input_argument))
    
        result_docs = []
        for hit in es_results['hits']['hits']:
            result_docs.append(hit['_source'])
    
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
                        "type": "best_fields"
                    }
                },

                     }
                    }
                        }
        return _search_query
class ElasticSemanticSearcher(ElasticSearcher):
    
    def search_query(self, input_argument):
        knn = {
        'field': 'vague_embedding',
        'query_vector': input_argument,
        'num_candidates': 100,
        'k':5
        }
        _search_query = {'knn': knn,
                    '_source': ['vague', 'actual', 'id']
                    }    
        return _search_query
    