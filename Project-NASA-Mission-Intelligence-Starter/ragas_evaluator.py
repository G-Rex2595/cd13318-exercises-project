
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from typing import Dict, List, Optional

# RAGAS imports
try:
    from ragas import SingleTurnSample, EvaluationDataset
    from ragas.metrics import BleuScore, NonLLMContextPrecisionWithReference, ResponseRelevancy, Faithfulness, RougeScore
    from ragas import evaluate
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False

def evaluate_response_quality(question: str, answer: str, contexts: List[str]) -> Dict[str, float]:
    """Evaluate response quality using RAGAS metrics"""
    if not RAGAS_AVAILABLE:
        return {"error": "RAGAS not available"}
    
    # TODO: Create evaluator LLM with model gpt-3.5-turbo
    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-3.5-turbo", base_url="https://openai.vocareum.com/v1"))
    # TODO: Create evaluator_embeddings with model test-embedding-3-small
    evaluator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(model="text-embedding-3-small", base_url="https://openai.vocareum.com/v1"))
    # TODO: Define an instance for each metric to evaluate
    metrics = [
        BleuScore(),
        NonLLMContextPrecisionWithReference(),
        ResponseRelevancy(),
        Faithfulness(),
        RougeScore()
    ]
    # TODO: Evaluate the response using the metrics
    try:
        evaluation_results = evaluate(
            dataset=EvaluationDataset(samples=[SingleTurnSample(
                user_input=question,
                response=answer,
                retrieved_contexts=contexts,
                reference_contexts=contexts,
                reference=str(contexts),
            )]),
            llm=evaluator_llm,
            embeddings=evaluator_embeddings,
            metrics=metrics,
            raise_exceptions=True
        )
    except Exception as e:
        return {"error": f"Evaluation failed: {str(e)}"}
    # TODO: Return the evaluation results
    return evaluation_results.scores[0]
