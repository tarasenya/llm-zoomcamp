"""
Generates ground truth data.
"""

import asyncio
import json
import pickle
from pathlib import Path

import aiohttp
import loguru
import pandas as pd
import tenacity
from dotenv import find_dotenv
from dotenv import load_dotenv
from openai import AsyncOpenAI
from tqdm.asyncio import tqdm_asyncio


logger = loguru.logger

load_dotenv(find_dotenv())

client = AsyncOpenAI()

# Rate limiting settings
MAX_CONCURRENT_REQUESTS = 5  # Adjust based on your API limits
REQUEST_INTERVAL = 0.5  # Time in seconds between requests
MAX_RETRIES = 3  # Maximum number of retries for a failed request
RETRY_DELAY = 2  # Delay between retries in seconds

prompt_template_for_generating_gt = """
You are an AI assistant tasked with creating slight variations of IT manager statements.
Your job is to take a vague, jargon-filled IT statement and create 5 slightly modified 
versions of it.

Guidelines:
1. Keep the overall structure and tone of the original statement.
2. Make minor changes to wording, but maintain the same level of jargon and vagueness.
3. Preserve any tech terminology, buzzwords, or acronyms present in the original.
4. Ensure the core meaning remains intact.
5. Aim for variations that an IT manager might use interchangeably in different 
conversations.

The original vague IT statement:
{question}

Provide the output as a list of 5 Python strings in parsable JSON format, like this:
["variant_1", "variant_2", "variant_3", "variant_4", "variant_5"]

Do not include additional information or code blocks.

Remember, the goal is to create statements that are very similar to the original, with 
only minor variations. They should all sound like they could have been said by the same 
IT manager in slightly different contexts.

Example:
Original: "Lets put our ducks in a row and get this cluster untangled before it 
goes pear-shaped."
Variations:
[
  "We need to get our ducks in a row and untangle this cluster before it 
  goes pear-shaped.",
  "Time to line up our ducks and sort out this cluster before we hit pear-shaped 
  territory.",
  "Lets align our ducks and detangle this cluster situation before pear-shaped becomes 
  our reality.",
  "We should organize our ducks and unravel this cluster mess before pear-shaped is on 
  the horizon.",
  "Its crucial we arrange our ducks and resolve this cluster tangle before pear-shaped 
  strikes."
]
""".strip()


@tenacity.retry(
    stop=tenacity.stop_after_attempt(MAX_RETRIES),
    wait=tenacity.wait_fixed(RETRY_DELAY),
    retry=tenacity.retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
    before_sleep=lambda retry_state: print(
        f"Retrying after error: {retry_state.outcome.exception()}"
    ),
)
async def generate_ground_truth_statement(question, semaphore):
    async with semaphore:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": prompt_template_for_generating_gt.format(
                            question=question
                        ),
                    }
                ],
            )
            await asyncio.sleep(REQUEST_INTERVAL)  # Add delay between requests
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in generate_ground_truth_statement: {e}")
            raise  # Re-raise the exception to trigger a retry


async def process_document(doc, semaphore):
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            generated = await generate_ground_truth_statement(doc["vague"], semaphore)
            generated = generated.replace("```", "").strip()
            parsed = json.loads(generated)
            if isinstance(parsed, list) and len(parsed) == 5:
                return doc["id"], generated
            else:
                print(f"Invalid response format for document {doc['id']}, \
                      attempt {attempt + 1}")
        except json.JSONDecodeError:
            print(f"JSON decode error for document {doc['id']}, attempt {attempt + 1}")
        except Exception as e:
            print(f"Unexpected error for document {doc['id']}, attempt {attempt + 1}: \
                {e}")

        if attempt < max_attempts - 1:
            await asyncio.sleep(REQUEST_INTERVAL)

    print(f"Failed to process document {doc['id']} after {max_attempts} attempts")
    return doc["id"], None


async def generate_ground_truth_csv_file(data):
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    gt_doc_id_vague = {}
    tasks = [process_document(doc, semaphore) for doc in data]

    for task in tqdm_asyncio.as_completed(tasks, total=len(tasks)):
        doc_id, result = await task
        if result is not None:
            gt_doc_id_vague[doc_id] = result

    with open(Path().cwd().parents[0] / "data" / "gt_doc_id_vague.pkl", "wb") as f:
        pickle.dump(gt_doc_id_vague, f)

    parsed_results = {
        doc_id: json.loads(json_questions)
        for doc_id, json_questions in gt_doc_id_vague.items()
    }

    final_results = [
        (vague_statement, doc_id)
        for doc_id, vague_statements in parsed_results.items()
        for vague_statement in vague_statements
    ]

    pd.DataFrame(final_results, columns=["vague", "doc_id"]).to_csv(
        Path().cwd().parents[0] / "data" / "ground_truth_data.csv", index=False
    )


async def main():
    with open(Path().cwd().parents[0] / "data" / "initial_data_w_id.json", "r") as f:
        data = json.load(f)
    await generate_ground_truth_csv_file(data)


if __name__ == "__main__":
    asyncio.run(main())
