import asyncio
import os
from data_ingestion import main_semantic_search
from db import init_db, create_user_and_db
from dotenv import load_dotenv

if os.path.exists('../.env'):
    load_dotenv('../.env')  
    ELASTIC_URL = os.getenv("ELASTIC_URL_LOCAL")
else:
    ELASTIC_URL = os.getenv('ELASTIC_URL')    
    
MODEL_NAME = os.getenv("MODEL_NAME")
INDEX_NAME = os.getenv("INDEX_NAME")


def main():
    # you may consider to comment <start>
    # if you just want to init the db or didn't want to re-index
    print("Starting the indexing process...")
    #asyncio.run(main_semantic_search(model_name='all-mpnet-base-v2',
    #                                 index_name='vague-actual-mpnet',
    #                                 dims=768,
    #                                 es_host=ELASTIC_URL))
    print("Initializing database...")
    create_user_and_db()
    init_db()

    print("Indexing process completed successfully!")


if __name__ == "__main__":
    main()