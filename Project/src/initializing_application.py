import asyncio
import os
from data_ingestion import main_semantic_search
from db import init_db, create_user_and_db
from dotenv import load_dotenv
from loguru import logger 

if os.path.exists('../.env'):
    load_dotenv('../.env')  
    ELASTIC_URL = os.getenv("ELASTIC_URL_LOCAL")
else:
    ELASTIC_URL = os.getenv('ELASTIC_URL')    
    
def main():
    logger.info("Starting the indexing process...")
    asyncio.run(main_semantic_search(model_name=os.getenv("MODEL_NAME"),
                                     index_name=os.getenv("INDEX_NAME"),
                                     dims=768,
                                     es_host=ELASTIC_URL))
    logger.info("Indexing process completed successfully!")
    logger.info("Initializing database...")
    create_user_and_db()
    init_db()
    logger.info('Database Operations completed.')
    
if __name__ == "__main__":
    main()