from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
from abc import ABC, abstractmethod
from typing import Any

from src.elastic_search_engine import ElasticKeywordSearcher

load_dotenv(find_dotenv('../.env'))

class AbstractRAG(ABC):
    
    def __init__(self, elastic_searcher: ElasticKeywordSearcher,
                 prompt_template: str, llm_model: Any):
        self.elastic_searcher = elastic_searcher
        self.prompt_template = prompt_template
        self.llm_model = llm_model
    
    @abstractmethod
    def build_prompt(query: str, search_result: list):
        ...
        
    @abstractmethod
    def llm(*args, **kwargs):
        ...
    
    def rag_results(self, vague):
        search_results = self.elastic_searcher.search(input_argument=vague)
        prompt = self.build_prompt(vague, search_results=search_results)
        answer = self.llm(prompt)
        return answer    

class ChatGPTRAG(AbstractRAG):
    client = OpenAI()
      
    def build_prompt(self, query, search_results):
       
        context = ''
        for doc in search_results:
            context+= f"vague: {doc['vague']}\nactual: {doc['actual']}\n\n"
        prompt = self.prompt_template.format(vague=query, context=context)    
        return prompt    
            
    def llm(self, prompt):
        response = self.client.chat.completions.create(model=self.llm_model,
                                             messages=[{'role': 'user', 'content': prompt}],)
        return response.choices[0].message.content    
    
        