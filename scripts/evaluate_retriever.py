import json
from langchain_core.documents import Document
from modules.utils import rerank_documents
from sentence_transformers import CrossEncoder
from hazm import word_tokenize
import numpy as np

def load_test_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_retriever(test_data, chunks, cross_encoder):
    precision_scores = []
    recall_scores = []
    f1_scores = []

    for item in test_data:
        query = item["question"]
        ground_truth = item["context"]

        # Create a list of documents (ground truth + distractors)
        docs = [Document(page_content=ground_truth, metadata={"chunk_index": 0})] + chunks[:10]
        retrieved_docs = rerank_documents(query, docs, chunks, cross_encoder)

        # Calculate metrics
        retrieved_texts = [doc.page_content for doc in retrieved_docs]
        relevant = ground_truth in retrieved_texts
        retrieved_count = len(retrieved_texts)
        relevant_retrieved = 1 if relevant else 0

        precision = relevant_retrieved / retrieved_count if retrieved_count > 0 else 0
        recall = relevant_retrieved / 1  # Only one relevant document
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        precision_scores.append(precision)
        recall_scores.append(recall)
        f1_scores.append(f1)

    return {
        "precision": np.mean(precision_scores),
        "recall": np.mean(recall_scores),
        "f1": np.mean(f1_scores)
    }

if __name__ == "__main__":
    # Example usage (replace with actual chunks and cross_encoder)
    test_data = load_test_data("../data/test_data.json")
    chunks = [Document(page_content="متن غیرمرتبط", metadata={"chunk_index": i}) for i in range(10)]
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    metrics = evaluate_retriever(test_data, chunks, cross_encoder)
    print(f"Precision: {metrics['precision']:.2f}")
    print(f"Recall: {metrics['recall']:.2f}")
    print(f"F1 Score: {metrics['f1']:.2f}")