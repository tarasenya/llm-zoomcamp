"""
Vague Interpreter Streamlit Application
=======================================

This module implements a Streamlit-based web application that interprets vague statements
using different language models. It allows users to input vague statements, processes them
using selected models, and provides interpretations. The application also includes a feedback
system and displays usage statistics.

The application uses Loguru for logging, Streamlit for the web interface, and interacts with
custom RAG (Retrieval-Augmented Generation) models and a judge LLM for evaluating responses.
It includes error handling for network issues and API problems.
"""

import sys
import streamlit as st
import time
import uuid
from loguru import logger
from typing import Dict, Any

from ambiguity_resolver_rag import ambiguity_resolver_rag
from phi_rag import phi3_rag
from judge_llm import JudgeLLM, LLMJudgementScore, JudgeLLMPromptInput
from database_operations.db import (
    save_conversation,
    save_feedback,
    get_feedback_stats,
)

# Import necessary exceptions
from requests.exceptions import RequestException
from openai import OpenAIError

def setup_logging():
    """
    Set up logging configuration for the application.

    This function removes any existing logger handlers and adds a new handler
    that writes to sys.stderr with a custom format. The log level is set to INFO,
    and logs are enqueued for thread-safety.
    """
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        enqueue=True,
    )

def init_session_state():
    """
    Initialize the Streamlit session state.

    This function sets up initial values for the conversation ID and feedback count
    in the Streamlit session state if they don't already exist.
    """
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "count" not in st.session_state:
        st.session_state.count = 0
        logger.info("Feedback count initialized to 0")

def process_user_input(user_input: str, model_choice: str) -> Dict[str, Any]:
    """
    Process the user's input using the selected model and judge LLM.

    :param user_input: The vague statement input by the user.
    :type user_input: str
    :param model_choice: The name of the selected model to use for processing.
    :type model_choice: str
    :return: A dictionary containing the processed answer, LLM judgement score,
             and response time. In case of an error, it contains an error message.
    :rtype: Dict[str, Any]
    :raises: RequestException, OpenAIError, Exception
    """
    logger.info(f"User asked: '{user_input}' using model {model_choice}")
    start_time = time.time()
    
    try:
        if model_choice == "openai/gpt-4o-mini":
            answer = ambiguity_resolver_rag.rag_results(vague=user_input)
        else:
            answer = phi3_rag.rag_results(vague=user_input)
        
        judge_llm = JudgeLLM()
        judge_llm_input: JudgeLLMPromptInput = {
            "vague": user_input,
            "translation": answer,
        }
        llm_judgement_score: LLMJudgementScore = judge_llm.judget_it(judge_llm_input)
        
        end_time = time.time()
        response_time = round(end_time - start_time, 2)
        logger.info(f"Answer received in {response_time} seconds")
        
        return {
            "answer": answer,
            "llm_judgement_score": llm_judgement_score,
            "response_time": response_time,
            "error": None
        }
    except RequestException as e:
        logger.error(f"Network error occurred: {str(e)}")
        return {"error": "Unable to connect to the language model server. Please check if the corresponding container has been started."}
    except OpenAIError as e:
        logger.error(f"OpenAI API error occurred: {str(e)}")
        return {"error": "An error occurred while accessing the OpenAI API. Check your OpenAI key"}
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        return {"error": "An unexpected error occurred. Please try again or contact support if the problem persists."}

def handle_feedback(feedback: int):
    """
    Handle user feedback for a conversation.

    This function updates the feedback count in the session state and saves the feedback
    to the database if a valid conversation ID exists.

    :param feedback: The feedback value (+1 for positive, -1 for negative).
    :type feedback: int
    """
    if st.session_state.conversation_id:
        st.session_state.count += feedback
        logger.info(f"Feedback received. New count: {st.session_state.count}")
        save_feedback(st.session_state.conversation_id, feedback)
        logger.info(f"{'Positive' if feedback > 0 else 'Negative'} feedback saved to database")
    else:
        st.error("Please ask a question before providing feedback.")

def main():
    """
    Main function to run the Streamlit application.

    This function sets up the Streamlit interface, handles user input, processes
    the input using the selected model, displays results, and manages user feedback.
    It also handles and displays any errors that occur during processing.
    """
    setup_logging()
    logger.info("Starting the vague interpreter")
    
    st.title("Vague Interpreter")
    init_session_state()

    model_choice = st.selectbox(
        "Select a model:",
        ["openai/gpt-4o-mini", "ollama/phi3"],
    )
    logger.info(f"User selected model: {model_choice}")

    user_input = st.text_input("Enter a vague statement from your boss:")

    if st.button("Ask"):
        st.session_state.conversation_id = str(uuid.uuid4())
        logger.info(f"New conversation started with ID: {st.session_state.conversation_id}")

        with st.spinner("Processing..."):
            result = process_user_input(user_input, model_choice)
            
            if result.get("error"):
                st.error(result["error"])
                logger.error(f"Error occurred: {result['error']}")
            else:
                st.success("Completed!")
                st.write(result["answer"])

                save_conversation(
                    conversation_id=st.session_state.conversation_id,
                    question=user_input,
                    answer=result["answer"],
                    model_used=model_choice,
                    llm_judgement_score=result["llm_judgement_score"],
                    response_time=result["response_time"],
                    timestamp=None,
                )
                logger.info("Conversation has been saved successfully.")

    # Feedback buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("+1"):
            handle_feedback(1)
    with col2:
        if st.button("-1"):
            handle_feedback(-1)

    st.write(f"Current count: {st.session_state.count}")

    # Display feedback stats
    feedback_stats = get_feedback_stats()
    st.subheader("Feedback Statistics")
    st.write(f"Thumbs up: {feedback_stats['thumbs_up']}")
    st.write(f"Thumbs down: {feedback_stats['thumbs_down']}")

    logger.info("Streamlit app loop completed")

if __name__ == "__main__":
    main()