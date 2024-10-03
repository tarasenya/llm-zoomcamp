"""
Artificial generation of initial data.
"""
import asyncio
import json
from pathlib import Path
from typing import Dict
from typing import List

import aiohttp
from dotenv import find_dotenv
from dotenv import load_dotenv
from loguru import logger
from openai import AsyncOpenAI


# Load environment variables
load_dotenv(find_dotenv())

# Initialize AsyncOpenAI client
client = AsyncOpenAI()

# Set up Loguru
logger.add("script_log.log", rotation="10 MB", level="INFO")

# Define the single prompt
PROMPT = """
Generate 50 pairs of sentences related to IT department management. For each pair:
1. The first sentence should mimic an IT department boss using slang, vague terminology, humor, and generally vague language. 
   This can cover topics like IT infrastructure, sales in the IT department, DevOps, software development, and product management.
2. The second sentence should clarify what the boss actually means in plain, direct language.

Important: Do not use any contractions or apostrophes in your sentences. For example, use "lets" instead of "let's", "dont" instead of "don't", etc.

Format the output as a valid JSON list of dictionaries, each with 'vague' and 'actual' keys.
Example:
[
    {
        "vague": "Lets put our ducks in a row and get this cluster untangled before it goes pear-shaped.",
        "actual": "We need to organize our project priorities and resolve the server issues before they cause major problems."
    },
    {
        "vague": "Time to juice up our pipeline and make it rain with those sweet sweet conversions.",
        "actual": "We need to improve our sales funnel and increase our conversion rates to boost revenue."
    }
]
"""

def safe_json_loads(content: str) -> List[Dict[str, str]]:
    # First, try to extract JSON from markdown
    logger.info(content)
    content = content.replace('```json', '').replace('```', '')
    try:
        parsed_content = json.loads(content)
        return parsed_content
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {str(e)}")
        return []  # Return an empty list instead of None

async def generate_chat_response(prompt: str, session: aiohttp.ClientSession) -> List[Dict[str, str]]:
    try:
        logger.info("Sending request to OpenAI API")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant that generates pairs of IT-related sentences as specified. Always return a valid JSON list of dictionaries. Do not use contractions or apostrophes."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content
        logger.success("Received response from OpenAI API")
        parsed_content = safe_json_loads(content)
        logger.info(f"Parsed {len(parsed_content)} items from API response")
        return parsed_content
    except Exception as e:
        logger.exception(f"An error occurred during API call: {str(e)}")
        return []

async def generate_all_responses(num_requests: int) -> List[Dict[str, str]]:
    async with aiohttp.ClientSession() as session:
        logger.info(f"Starting {num_requests} API requests")
        tasks = [generate_chat_response(PROMPT, session) for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
    flattened_results = [item for sublist in results for item in sublist if isinstance(item, dict) and 'vague' in item and 'actual' in item]
    logger.success(f"Generated a total of {len(flattened_results)} valid sentence pairs")
    return flattened_results

@logger.catch
async def main():
    logger.info("Script started")
    
    # Number of requests to make (20 requests * 50 pairs each = 1000 total pairs)
    num_requests = 20

    logger.info("Generating IT department sentences...")
    it_vocabulary = await generate_all_responses(num_requests)

    # Save the combined data to a JSON file
    output_path = Path().cwd().parent / 'data' / 'initial_data.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open('w', encoding='utf-8') as file:
        json.dump(it_vocabulary, file, indent=2, ensure_ascii=False)

    logger.success(f"Data saved to {output_path}")
    logger.info(f"Total pairs generated: {len(it_vocabulary)}")
    logger.success("Script completed successfully")

if __name__ == "__main__":
    asyncio.run(main())