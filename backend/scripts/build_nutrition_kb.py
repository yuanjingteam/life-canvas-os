import os
import argparse
import sys
from typing import List

# Use mirror for Hugging Face to avoid connection issues in some regions
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# Ensure backend directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Default configuration from SDD
DEFAULT_DB_DIR = os.path.join(os.path.dirname(__file__), "..", "db", "vector_db")
DEFAULT_SOURCE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "nutrition_sources")
COLLECTION_NAME = "nutrition_knowledge_base"

# Recommended embedding model for Chinese nutrition terminology
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"

def build_kb(source_dir: str, db_dir: str):
    """
    Build the nutrition knowledge base from documents in source_dir.
    """
    print(f"[*] Starting Knowledge Base Construction...")
    print(f"[*] Source directory: {source_dir}")
    print(f"[*] Vector DB directory: {db_dir}")

    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
        print(f"[!] Source directory was missing, created: {source_dir}")
        print(f"[!] Please put your nutrition PDF/Markdown files in this folder and run again.")
        return

    # 1. Load Documents (PDF and Markdown/Text)
    print("[*] Loading documents...")
    # Using RapidOCR for PDF to handle scanned images
    loaders = [
        DirectoryLoader(source_dir, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'}),
        DirectoryLoader(source_dir, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'}),
        DirectoryLoader(source_dir, glob="**/*.pdf", loader_cls=PyPDFLoader, loader_kwargs={"extract_images": True})
    ]
    
    documents = []
    for loader in loaders:
        documents.extend(loader.load())
    
    if not documents:
        print("[!] No documents found in source directory. Aborting.")
        return

    print(f"[*] Loaded {len(documents)} documents.")

    # 2. Chunking Strategy (Semantic Chunking as per SDD)
    print("[*] Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""]
    )
    all_chunks = text_splitter.split_documents(documents)
    
    # --- Data Cleaning ---
    print("[*] Cleaning data (filtering trash chunks)...")
    import re
    cleaned_chunks = []
    for chunk in all_chunks:
        content = chunk.page_content.strip()
        # 1. Skip chunks that are too short (e.g., just a title or footer)
        if len(content) < 15: continue
        # 2. Skip chunks that are just numbers or non-alphabet/non-han (likely garbage)
        if re.match(r'^[\d\s\W]+$', content): continue
        # 3. Simple cleanup of multiple newlines/spaces
        content = re.sub(r'\n{3,}', '\n\n', content)
        chunk.page_content = content
        cleaned_chunks.append(chunk)
    
    print(f"[*] Original: {len(all_chunks)}, Cleaned: {len(cleaned_chunks)}")
    
    # --- Persistence ---
    # 3. Embedding Selection
    print(f"[*] Initializing embedding model: {EMBEDDING_MODEL}")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'}
    )

    # 4. Storage (Chroma)
    print(f"[*] Writing to Chroma DB: {db_dir}")
    from langchain_chroma import Chroma
    vector_db = Chroma.from_documents(
        documents=cleaned_chunks,
        embedding=embeddings,
        persist_directory=db_dir,
        collection_name=COLLECTION_NAME
    )
    
    # 5. Persist BM25 Index for Hybrid Search
    import pickle
    bm25_path = os.path.join(db_dir, "bm25_index.pkl")
    print(f"[*] Saving BM25 Index to: {bm25_path}")
    with open(bm25_path, "wb") as f:
        pickle.dump(cleaned_chunks, f)
    
    print("[+] Knowledge Base built with cleanup and Hybrid Search support.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Nutrition Knowledge Base (RAG)")
    parser.add_argument("--source", type=str, default=DEFAULT_SOURCE_DIR, help="Directory containing source documents")
    parser.add_argument("--db", type=str, default=DEFAULT_DB_DIR, help="Directory to store Vector DB")
    
    args = parser.parse_args()
    build_kb(args.source, args.db)
