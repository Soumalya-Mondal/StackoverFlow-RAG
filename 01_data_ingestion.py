import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

# Pricing for Azure OpenAI text-embedding-3-large (per 1M tokens)
EMBEDDING_COST_PER_1M_TOKENS = 0.02  # $0.02 per 1M tokens (input)
total_tokens_used = 0

def get_embedding_model():
    """Initialize and return Azure OpenAI embedding model"""
    return AzureOpenAIEmbeddings(
        api_key=os.getenv("API_KEY"),
        azure_endpoint=os.getenv("API_ENDPOINT"),
        model=os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-3-large"),
        api_version=os.getenv("API_VERSION", "2024-02-01")
    )

def estimate_tokens(text, model="text-embedding-3-large"):
    """
    Estimate token count for text.
    Rough estimate: ~4 characters = 1 token for embedding models
    """
    return max(1, len(text) // 4)

def calculate_cost(token_count):
    """Calculate the cost of tokens used"""
    return (token_count / 1_000_000) * EMBEDDING_COST_PER_1M_TOKENS

def load_documents(docs_path="docs"):
    """Load all text files from the docs directory"""
    global total_tokens_used
    print(f"Loading documents from {docs_path}...")

    # Check if docs directory exists
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"The directory {docs_path} does not exist. Please create it and add your company files.")

    # Load all .txt files from the docs directory
    loader = DirectoryLoader(
        path=docs_path,
        glob="*.txt",
        loader_cls=TextLoader
    )

    documents = loader.load()

    if len(documents) == 0:
        raise FileNotFoundError(f"No .txt files found in {docs_path}. Please add your company documents.")

    # Calculate tokens for loaded documents
    docs_tokens = sum(estimate_tokens(doc.page_content) for doc in documents)
    total_tokens_used += docs_tokens

    for i, doc in enumerate(documents[:2]):  # Show first 2 documents
        print(f"\nDocument {i+1}:")
        print(f"  Source: {doc.metadata['source']}")
        print(f"  Content length: {len(doc.page_content)} characters")
        print(f"  Estimated tokens: {estimate_tokens(doc.page_content)}")
        print(f"  Content preview: {doc.page_content[:100]}...")
        print(f"  metadata: {doc.metadata}")

    print(f"\n📊 Total tokens for all documents: {docs_tokens}")
    print(f"   Estimated cost: ${calculate_cost(docs_tokens):.6f}")

    return documents

def split_documents(documents, chunk_size=1000, chunk_overlap=0):
    """Split documents into smaller chunks with overlap"""
    global total_tokens_used
    print("Splitting documents into chunks...")

    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = text_splitter.split_documents(documents)

    # Calculate tokens for chunks (same as documents, but good to track separately)
    chunks_tokens = sum(estimate_tokens(chunk.page_content) for chunk in chunks)

    if chunks:

        for i, chunk in enumerate(chunks[:5]):
            print(f"\n--- Chunk {i+1} ---")
            print(f"Source: {chunk.metadata['source']}")
            print(f"Length: {len(chunk.page_content)} characters")
            print(f"Estimated tokens: {estimate_tokens(chunk.page_content)}")
            print(f"Content:")
            print(chunk.page_content)
            print("-" * 50)

        if len(chunks) > 5:
            print(f"\n... and {len(chunks) - 5} more chunks")

    print(f"\n📊 Total chunks created: {len(chunks)}")
    print(f"   Estimated tokens: {chunks_tokens}")

    return chunks

def create_vector_store(chunks, persist_directory="db/chroma_db"):
    """Create and persist ChromaDB vector store"""
    print("Creating embeddings and storing in ChromaDB...")

    embedding_model = get_embedding_model()

    # Create ChromaDB vector store
    print("--- Creating vector store ---")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"}
    )
    print("--- Finished creating vector store ---")

    print(f"Vector store created and saved to {persist_directory}")
    return vectorstore

def main():
    """Main ingestion pipeline"""
    global total_tokens_used
    print("=== RAG Document Ingestion Pipeline ===\n")

    # Define paths
    docs_path = "docs"
    persistent_directory = "db/chroma_db"

    # Check if vector store already exists
    if os.path.exists(persistent_directory):
        print("✅ Vector store already exists. No need to re-process documents.")

        embedding_model = get_embedding_model()
        vectorstore = Chroma(
            persist_directory=persistent_directory,
            embedding_function=embedding_model,
            collection_metadata={"hnsw:space": "cosine"}
        )
        print(f"Loaded existing vector store with {vectorstore._collection.count()} documents")
        return vectorstore

    print("Persistent directory does not exist. Initializing vector store...\n")

    # Step 1: Load documents
    documents = load_documents(docs_path)

    # Step 2: Split into chunks
    chunks = split_documents(documents)

    # # Step 3: Create vector store
    vectorstore = create_vector_store(chunks, persistent_directory)

    # Final token summary
    print(f"\n💰 === COST SUMMARY ===")
    print(f"   Total tokens processed: {total_tokens_used:,}")
    print(f"   Estimated cost: ${calculate_cost(total_tokens_used):.8f}")
    print(f"   Model: text-embedding-3-large")
    print(f"   Rate: ${EMBEDDING_COST_PER_1M_TOKENS}/1M tokens")
    print(f"\n✅ Ingestion complete! Your documents are now ready for RAG queries.")
    return vectorstore

if __name__ == "__main__":
    main()