""" Generate initial data for the project """
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import ast
import json
from pathlib import Path

load_dotenv(find_dotenv())

client = OpenAI()

def generate_chat_response(prompt):
    _system_general_prompt = 'Imagine you are a very busy team lead of an IT department, you always give very vague instructions or ask vague questions'
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _system_general_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        # Extract and return the response message content
        return response.choices[0].message.content
    
    except client.error.OpenAIError as e:
        return f"An error occurred: {str(e)}"


dev_ops_prompt = 'The IT boss now hat lots of troubles in DevOps sub department. Deployments are failing, environemtns are not stable. Generate 100 couples of the sentences of the following form, first sentence is what a boss says to his colleagues in a vague and very weird manner, the second sentence is what he actually means. I want to get this sentences in a format of list of dictionaries (The keys of dictionaries should be "vague", "actual"), so that I can use it immediately in python code, no additional information should be added.'
ml_prompt = 'The IT boss now hat lots of troubles with machine learning department. Customers are not satisfacted with models quality. Generate 100 couples of the sentences of the following form, first sentence is what a boss says to his colleagues in a vague and very weird manner, the second sentence is what he actually means. I want to get this sentences in a format of list of dictionaries (The keys of dictionaries should be "vague", "actual"), so that I can use it immediately in python code, no additional information should be added.'
marketing_prompt = 'The IT boss now hat lots of troubles with marketing department. Now all need to take part in marekting activities. Generate 100 couples of the sentences of the following form, first sentence is what a boss says to his colleagues in a vague and very weird manner, the second sentence is what he actually means. I want to get this sentences in a format of list of dictionaries (The keys of dictionaries should be "vague", "actual"), so that I can use it immediately in python code, no additional information should be added.'

sales_prompt = 'The IT bossnow hat lots of troubles with sales department. All the time he talks about selling our IT products. Generate 100 couples of the sentences of the following form, first sentence is what a boss says to his colleagues in a vague and very weird manner, the second sentence is what he actually means. I want to get this sentences in a format of list of dictionaries (The keys of dictionaries should be "vague", "actual"), so that I can use it immediately in python code, no additional information should be added.'
frontend_prompt = 'The IT boss now hat lots of troubles with frontend  developers. He gives pieces of advice hot to fix front end part, offers new frameworks. Generate 100 couples of the sentences of the following form, first sentence is what a boss says to his colleagues in a vague and very weird manner, the second sentence is what he actually means. I want to get this sentences in a format of list of dictionaries (The keys of dictionaries should be "vague", "actual"), so that I can use it immediately in python code, no additional information should be added.'
backend_prompt = 'The IT boss now hat lots of troubles with backend developers. He gives pieces of advice hot to fix back end part, offers new frameworks and programming languages. Generate 100 couples of the sentences of the following form, first sentence is what a boss says to his colleagues in a vague and very weird manner, the second sentence is what he actually means. I want to get this sentences in a format of list of dictionaries (The keys of dictionaries should be "vague", "actual"), so that I can use it immediately in python code, no additional information should be added.'

chat_responses = []
for user_prompt in [dev_ops_prompt, ml_prompt, marketing_prompt, sales_prompt, frontend_prompt, backend_prompt]:
    chat_response = generate_chat_response(user_prompt)
    chat_responses.append(chat_response) 

chef_vocabulary = []
for chat_response in chat_responses:
    cleaned_string = chat_response.replace('```python\nvague_instructions = ', '').replace('```python\nsentences = ', '').replace('```python\ndata = ', '').\
    replace('```', '').strip()
    chef_vocabulary.extend(ast.literal_eval(cleaned_string))

file_path = "data.json"

with open(Path().cwd().parent/'data'/'initial_data', 'w') as file:  
    json.dump(chef_vocabulary, file)




