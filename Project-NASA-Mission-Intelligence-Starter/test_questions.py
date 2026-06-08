from rag_client import discover_chroma_backends, initialize_rag_system, retrieve_documents, format_context
from llm_client import generate_response
import os

def main():
    with open(os.path.join(os.path.dirname(__file__), "evaluation_dataset.txt"), "r") as f:
        qa_pairs = f.read().strip().split("\n\n")

    chroma_backends = discover_chroma_backends()
    first_backend = next(iter(chroma_backends.items()))
    collection = initialize_rag_system(first_backend[1]["directory"], first_backend[1]["collection_name"])
    if collection[1] is False:
        print(f"Error initializing RAG system: {collection[2]}")
        return
    collection = collection[0]

    dataset = []
    for item in qa_pairs:
        question, answer = item.split("\n")
        question = question.replace("Question: ", "")
        answer = answer.replace("Response: ", "")
        dataset.append((question, answer))
    
    for question, answer in dataset:
        print(f"Question: {question}")
        documents = retrieve_documents(collection, question, n_results=3)
        for doc, metadata in zip(documents["documents"][0], documents["metadatas"][0]):
            print(f"-->Retrieved Document: {doc}")
            print()
            print(f"-->Metadata: {metadata}")
            print("\n")
        context = format_context(documents["documents"][0], documents["metadatas"][0])
        print(f"-->Formatted Context: {context}")
        print("\n")
        response = generate_response(os.getenv("OPENAI_API_KEY"), question, context, conversation_history=[])
        print(f"Generated Response: {response}")
        print(f"Expected Answer: {answer}")
        print("-" * 50)
        print("\n")

if __name__ == "__main__":
    main()