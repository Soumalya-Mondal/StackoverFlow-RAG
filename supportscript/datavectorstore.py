# define "data_vector_store" function
def data_vector_store(csv_file_path: str) -> dict:
    # Importing Python Module:S1
    try:
        import os
        from pathlib import Path
        from langchain_openai import AzureOpenAIEmbeddings
        import pandas
        from langchain_core.documents import Document
        from langchain_chroma import Chroma
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataVectorStore:S1] - {error}'}

    # Loading and Validating Environment Variables and Define Azure OpenAI Embedding Model:S2
    try:
        AZURE_API_ENDPOINT = os.getenv('AZURE_API_ENDPOINT')
        AZURE_API_KEY = os.getenv('AZURE_API_KEY')
        AZURE_API_EMBEDDING_DEPLOYMENT_NAME = os.getenv('AZURE_API_EMBEDDING_DEPLOYMENT_NAME')
        AZURE_API_VERSION = os.getenv('AZURE_API_VERSION')
        PERSIST_DIRECTORY = os.getenv('PERSIST_DIRECTORY', 'kbdb')
        COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'csv_questions')

        # Define required environment variables
        required_env_vars = {
            'AZURE_OPENAI_ENDPOINT': AZURE_API_ENDPOINT,
            'AZURE_OPENAI_API_KEY': AZURE_API_KEY,
            'AZURE_OPENAI_EMBEDDING_DEPLOYMENT': AZURE_API_EMBEDDING_DEPLOYMENT_NAME,
            'AZURE_OPENAI_API_VERSION': AZURE_API_VERSION
        }
        # Check for missing or empty environment variables
        missing_vars = []
        for var_name, var_value in required_env_vars.items():
            if var_value is None or (isinstance(var_value, str) and var_value.strip() == ''):
                missing_vars.append(var_name)
        # Return error if any required variables are missing
        if missing_vars:
            return {'status': 'ERROR', 'message': f'ERROR - [DataVectorStore:S2] - Missing Required Environment Variables: {", ".join(missing_vars)}'}
        # Define Azure OpenAI Embedding Model
        azure_embedding_object = AzureOpenAIEmbeddings(
            azure_endpoint = AZURE_API_ENDPOINT,
            api_key = AZURE_API_KEY,
            openai_api_version = AZURE_API_VERSION,
            azure_deployment = AZURE_API_EMBEDDING_DEPLOYMENT_NAME
        )
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataVectorStore:S2] - {error}'}

    # Check If Vector Store Already Exists:S3
    try:
        chroma_db_file_path = Path(PERSIST_DIRECTORY) / 'chroma.sqlite3'
        if chroma_db_file_path.exists():
            return {'status': 'SUCCESS', 'message': 'Vector Store Already Exists'}
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataVectorStore:S3] - {error}'}

    # Load CSV as Documents:S4
    try:
        df = pandas.read_csv(csv_file_path)
        required_cols = {'question_title', 'question_id'}
        if not required_cols.issubset(set(df.columns)):
            raise ValueError(f"CSV must contain columns {required_cols}, found: {list(df.columns)}")
        documents = []
        for row in df.itertuples(index = True):
            text_val = str(row.question_title) if pandas.notna(row.question_title) else ""
            qid_val = row.question_id

            doc = Document(
                page_content = text_val,
                metadata={
                    'question_id': int(qid_val) if pandas.notna(qid_val) else None,
                    "row_index": int(row.Index),
                    "source": os.path.basename(csv_file_path),
                }
            )
            documents.append(doc)
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataVectorStore:S4] - {error}'}

    # Create Vector Store from Documents:S5
    try:
        Chroma.from_documents(
            documents = documents,
            embedding = azure_embedding_object,
            persist_directory = PERSIST_DIRECTORY,
            collection_name = COLLECTION_NAME,
            collection_metadata = {'hnsw:space': 'cosine'}
        )
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataVectorStore:S5] - {error}'}

    # Verify Vector Store Database File Created:S6
    try:
        chroma_db_file_path = Path(PERSIST_DIRECTORY) / 'chroma.sqlite3'
        if not chroma_db_file_path.exists():
            return {'status': 'ERROR', 'message': 'ERROR - [DataVectorStore:S6] - Chroma Database File Not Found'}
        return {'status': 'SUCCESS', 'message': 'Vector Store Created Successfully'}
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataVectorStore:S6] - {error}'}