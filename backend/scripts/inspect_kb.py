import os
import sys

# Use mirror for Hugging Face
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# Ensure backend directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "db", "vector_db"))
embedding_model = "BAAI/bge-small-zh-v1.5"

def inspect_db():
    print(f"[*] Connecting to Chroma DB at: {db_dir}")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model,
        model_kwargs={'device': 'cpu'}
    )
    
    db = Chroma(
        persist_directory=db_dir,
        embedding_function=embeddings,
        collection_name="nutrition_knowledge_base"
    )
    
    results = db.get()
    docs = results["documents"]
    metadatas = results["metadatas"]
    
    print(f"[*] Total chunks found: {len(docs)}")
    print("-" * 50)
    
    for i, (doc, meta) in enumerate(zip(docs, metadatas)):
        print(f"Chunk {i+1} (Source: {meta.get('source', 'unknown')}):")
        print(doc)
        print("-" * 50)

if __name__ == "__main__":
    inspect_db()
