import os

from openai import OpenAI
from abc import ABC, abstractmethod
from typing import Any
from sentence_transformers import SentenceTransformer

from elastic_search_engine import ElasticKeywordSearcher


class AbstractRAG(ABC):
    
    def __init__(self, elastic_searcher: ElasticKeywordSearcher,
                 prompt_template: str, sentence_transformer_name: str, llm_model: Any):
        self.elastic_searcher = elastic_searcher
        self.prompt_template = prompt_template
        self.llm_model = llm_model
        self.sentence_transformer = None
        if sentence_transformer_name:
            self.sentence_transformer = SentenceTransformer(sentence_transformer_name)
    
    @abstractmethod
    def build_prompt(query: str, search_result: list):
        ...
        
    @abstractmethod
    def llm(*args, **kwargs):
        ...
    
    def rag_results(self, vague):
        if self.sentence_transformer:
            input_argument = self.sentence_transformer.encode(vague)
        else:
            input_argument = vague    
        search_results = self.elastic_searcher.search(input_argument=input_argument)
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
        _message = response.choices[0].message.content
        return _message
    
class OllamaRag(ChatGPTRAG):
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/v1/")
    client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")