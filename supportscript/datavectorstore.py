import os
import pandas as pd
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# -----------------------------
# Config (edit via .env or defaults)
# -----------------------------
CSV_PATH = os.getenv("CSV_PATH", "sampletestdata.csv")

# CSV column names
TEXT_COLUMN = os.getenv("CSV_TEXT_COLUMN", "question_title")  # embed ONLY this
ID_COLUMN = os.getenv("CSV_ID_COLUMN", "question_id")         # store as metadata

# Chroma persistence
PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "db/chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "csv_questions")


def get_embedding_model():
    """
    Initialize Azure OpenAI embedding model.

    Supports env var names in BOTH styles:
      Old-style:
        API_KEY, API_ENDPOINT, API_VERSION, EMBEDDING_DEPLOYMENT (or EMBEDDING_MODEL_NAME as deployment name)
      Recommended-style:
        AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    """

    api_key = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("API_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION") or os.getenv("API_VERSION") or "2024-02-15-preview"

    # Azure requires the *deployment name* for embeddings
    deployment = (
        os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        or os.getenv("EMBEDDING_DEPLOYMENT")
        or os.getenv("EMBEDDING_MODEL_NAME")  # fallback if you stored deployment name here
    )

    if not api_key or not endpoint or not deployment:
        raise ValueError(
            "Missing Azure OpenAI settings. Please set:\n"
            "- AZURE_OPENAI_API_KEY (or API_KEY)\n"
            "- AZURE_OPENAI_ENDPOINT (or API_ENDPOINT)\n"
            "- AZURE_OPENAI_EMBEDDING_DEPLOYMENT (or EMBEDDING_DEPLOYMENT / EMBEDDING_MODEL_NAME as deployment name)\n"
        )

    return AzureOpenAIEmbeddings(
        azure_endpoint=endpoint,
        api_key=api_key,
        openai_api_version=api_version,
        azure_deployment=deployment
    )


def load_csv_as_documents(csv_path: str):
    """
    Load CSV rows as LangChain Documents:
      - page_content = TEXT_COLUMN (embedded)
      - metadata contains ID_COLUMN (returned later; NOT embedded)
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    print(f"Loading CSV: {csv_path}")
    df = pd.read_csv(csv_path)

    # Validate required columns
    required_cols = {TEXT_COLUMN, ID_COLUMN}
    if not required_cols.issubset(set(df.columns)):
        raise ValueError(
            f"CSV must contain columns {required_cols}, found: {list(df.columns)}"
        )

    documents = []
    for idx, row in df.iterrows():
        text_val = str(row[TEXT_COLUMN]) if pd.notna(row[TEXT_COLUMN]) else ""
        qid_val = row[ID_COLUMN]

        doc = Document(
            page_content=text_val,  # <-- ONLY this is embedded
            metadata={
                ID_COLUMN: int(qid_val) if pd.notna(qid_val) else None,
                "row_index": int(idx),
                "source": os.path.basename(csv_path),
            }
        )
        documents.append(doc)

    print(f"✅ Loaded {len(documents)} rows as documents.")

    # Small preview
    for i, doc in enumerate(documents[:3]):
        print(f"\n--- Preview Document {i+1} ---")
        print(f"Metadata: {doc.metadata}")
        print(f"Content: {doc.page_content[:200]}")

    return documents


def create_vector_store(documents, persist_directory: str):
    """
    Create and persist ChromaDB vector store from documents.
    """
    print("\nCreating embeddings and storing in ChromaDB...")
    embedding_model = get_embedding_model()

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_name=COLLECTION_NAME,
        collection_metadata={"hnsw:space": "cosine"}
    )

    try:
        print(f"✅ Vector store created. Stored documents: {vectorstore._collection.count()}")
    except Exception:
        print("✅ Vector store created.")

    print(f"📌 Persisted at: {persist_directory}")
    return vectorstore


def load_vector_store(persist_directory: str):
    """
    Load an existing ChromaDB vector store.
    """
    print("✅ Vector store already exists. Loading from disk...")
    embedding_model = get_embedding_model()

    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_model,
        collection_name=COLLECTION_NAME
    )

    try:
        print(f"Loaded vector store with {vectorstore._collection.count()} documents")
    except Exception:
        print("Loaded vector store.")
    return vectorstore


def main():
    print("=== CSV → Chroma Ingestion Pipeline (No Splitter, No Cost Calc) ===\n")

    # Load existing DB if present & non-empty
    if os.path.exists(PERSIST_DIR) and os.path.isdir(PERSIST_DIR) and len(os.listdir(PERSIST_DIR)) > 0:
        load_vector_store(PERSIST_DIR)
        print("\nℹ️ No re-ingestion performed.")
        return

    print("Persistent directory does not exist or is empty. Creating new vector store...\n")

    # Step 1: Load CSV as Documents (embed ONLY question_title, store question_id)
    documents = load_csv_as_documents(CSV_PATH)

    # Step 2: Store in Chroma (no chunking)
    create_vector_store(documents, PERSIST_DIR)

    print("\n✅ Ingestion complete! CSV rows are now stored in ChromaDB.")


if __name__ == "__main__":
    main()