import llm
import re

class JudgeLLM:
    judge_prompt_template = """ 
    LLM-as-a-Judge Prompt for RAG Evaluation
    You are an expert judge evaluating the performance of a Retrieval-Augmented Generation (RAG) system. This system is designed to translate vague statements from IT bosses into their actual meanings. Your task is to assess the quality and accuracy of the RAG system's translations.
    For each example, you will be provided with:

    The original vague statement or question from the IT boss
    The RAG system's translation

    Input Data
    Please evaluate the following translation:
    Vague IT boss question: {vague}
    RAG Translation: {translation}

    Evaluation Criteria
    Your job is to:

    Analyze the RAG system's translation.
    Evaluate the translation on the following criteria:
    a. Accuracy: How well does the translation capture the intended meaning?
    b. Clarity: Is the translation clear and easy to understand?
    c. Completeness: Does the translation cover all important aspects of the actual meaning?
    d. Relevance: Does the translation focus on the most important parts of the vague statement?
    Provide a score for each criterion on a scale of 1-5, where:
    1 = Poor
    2 = Fair
    3 = Good
    4 = Very Good
    5 = Excellent
    Give an overall score (1-5) for the translation.
    Provide a brief explanation (2-3 sentences) for your scoring, highlighting strengths and areas for improvement.
    If the translation is incorrect or misleading, explain what went wrong and suggest how it could be improved.

    Output Format
    Please structure your evaluation like this:
    Criteria Scores:

    Accuracy: [Score]
    Clarity: [Score]
    Completeness: [Score]
    Relevance: [Score]

    Overall Score: [Score]
    Explanation: [Your brief explanation]
    Improvement Suggestions (if necessary): [Your suggestions]
    Please provide your evaluation for the given example.
    """.strip()
    
    @staticmethod
    def parse_evaluation_text(text: str) -> dict:
        """

        Args:
            text str: answer got from Judge-LLM (gpt-5o-mini)

        Returns:
            dict: of the following format  {'Criteria Scores': {'Clarity':..., 'Relevance':..., 'Accuracy':..., 'Completeness':...}, 'Overall Score': ...,
            'Explanation':..., 'Imporvement Suggestions': ...}
        """
        # Initialize the dictionary
        result = {"Criteria Scores": {}}
        
        # Use regex to extract key-value pairs
        patterns = {
            "Criteria Scores": r'(\w+):\s*(\d+)',
            "Overall Score": r'Overall Score:\s*([\d.]+)',
            "Explanation": r'Explanation:\s*(.*?)(?=\n\n|\Z)',
            "Improvement Suggestions": r'Improvement Suggestions:\s*(.*?)(?=\n\n|\Z)'
        }
        
        # Extract Criteria Scores
        criteria_scores = re.findall(patterns["Criteria Scores"], text)
        for criterion, score in criteria_scores:
            result["Criteria Scores"][criterion] = int(score)
        
        # Extract other fields
        for key, pattern in patterns.items():
            if key != "Criteria Scores":
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    value = match.group(1).strip()
                    result[key] = float(value) if key == "Overall Score" else value
        
        return result

    def judget_it(self, rec):
            judge_prompt = self.judge_prompt_template.format(**rec)
            answer = llm.llm(prompt=judge_prompt, gpt_model='gpt-4o-mini')
            return self.parse_evaluation_text(answer)
