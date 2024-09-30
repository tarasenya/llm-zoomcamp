import streamlit as st
import time
import uuid

from ambiguity_resolver_rag import ambiguity_resolver_rag
from phi_rag import phi3_rag
from judge_llm import JudgeLLM, LLMJudgementScore, JudgeLLMPromptInput
from database_operations.db import (
    save_conversation,
    save_feedback,
    get_feedback_stats,
)


def print_log(message):
    print(message, flush=True)


def main():
    judge_llm = JudgeLLM()
    print_log("Starting the vague interpretator")
    st.title("Vague Intepretator")

    # Session state initialization
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "count" not in st.session_state:
        st.session_state.count = 0
        print_log("Feedback count initialized to 0")

    # Model selection
    model_choice = st.selectbox(
        'Select a model:',
        ['openai/gpt-4o-mini',
         'ollama/phi3'],
    )
    print_log(f"User selected model: {model_choice}")

    # User input
    user_input = st.text_input("Enter a vague statement from your boss:")

    if st.button("Ask"):
        # Generate a new conversation ID when asking a question
        st.session_state.conversation_id = str(uuid.uuid4())
        print_log(
            f"New conversation started with ID: {st.session_state.conversation_id}"
        )

        print_log(f"User asked: '{user_input}'")
        with st.spinner("Processing..."):
            print_log(f"Getting answer from assistant using {model_choice}.")
            start_time = time.time()
            if model_choice == 'openai/gpt-4o-mini':
                _answer = ambiguity_resolver_rag.rag_results(vague=user_input)
            else:
                _answer = phi3_rag.rag_results(vague=user_input)    
            _judge_llm_input: JudgeLLMPromptInput = {
                "vague": user_input,
                "translation": _answer,
            }
            _llm_judgement_score: LLMJudgementScore = judge_llm.judget_it(
                _judge_llm_input
            )
            print_log(_llm_judgement_score)
            end_time = time.time()
            print_log(f"Answer received in {end_time - start_time:.2f} seconds")
            st.success("Completed!")
            st.write(_answer)

            # Save conversation to database
            print_log("Saving conversation to database")
            save_conversation(
                conversation_id=st.session_state.conversation_id,
                question=user_input,
                answer=_answer,
                model_used=model_choice,
                llm_judgement_score=_llm_judgement_score,
                response_time=round(end_time - start_time, 2),
                timestamp=None,
            )
            print_log("Conversation saved successfully")

    # Feedback buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("+1"):
            if st.session_state.conversation_id:
                st.session_state.count += 1
                print_log(
                    f"Positive feedback received. New count: {st.session_state.count}"
                )
                save_feedback(st.session_state.conversation_id, 1)
                print_log("Positive feedback saved to database")
            else:
                st.error("Please ask a question before providing feedback.")

    with col2:
        if st.button("-1"):
            if st.session_state.conversation_id:
                st.session_state.count -= 1
                print_log(
                    f"Negative feedback received. New count: {st.session_state.count}"
                )
                save_feedback(st.session_state.conversation_id, -1)
                print_log("Negative feedback saved to database")
            else:
                st.error("Please ask a question before providing feedback.")

    st.write(f"Current count: {st.session_state.count}")

    # Display feedback stats
    feedback_stats = get_feedback_stats()
    st.subheader("Feedback Statistics")
    st.write(f"Thumbs up: {feedback_stats['thumbs_up']}")
    st.write(f"Thumbs down: {feedback_stats['thumbs_down']}")

    print_log("Streamlit app loop completed")


if __name__ == "__main__":
    print_log("Vague Translator application started")
    main()
