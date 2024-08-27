from typing import Dict, List, Union

import numpy as np
from elasticsearch import Elasticsearch

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def elastic_search(es_client,index_name,  query, size, filter_condition = {"filter":{}}):
    must_condition = {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^4", "text"],
                        "type": "best_fields"
                                   }
                       }
                    }
    if filter_condition["filter"] != {}:
        must_condition.update(filter_condition)
    
    search_query = {
        "size": size,
        "query": {
            "bool": {
                **must_condition,
            }
        }
    }

    response = es_client.search(index=index_name, body=search_query)
    
    result_docs = []
    
    for hit in response['hits']['hits']:
        result_docs.append({'score': hit['_score'], 'source': hit['_source']})
    
    return result_docs

@data_loader
def search(*args, **kwargs) -> List[Dict]:
    connection_string = kwargs.get('connection_string', 'http://localhost:9200')
    index_name = kwargs.get('index_name')
    print('index name=======================')
    print(index_name)
    top_k = kwargs.get('top_k', 5)
    query = "When is the next cohort?"


    es_client = Elasticsearch(connection_string)
    
    result = elastic_search(es_client, index_name, query,  top_k)
    print(result)

    return result


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'