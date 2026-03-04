# define "data_vector_store" function
def data_vector_store(csv_file_path: str) -> dict:
    # Importing Python Module:S1
    try:
        import os
        from langchain_openai import AzureOpenAIEmbeddings
        import pandas as pd
        from langchain_core.documents import Document
        from langchain_chroma import Chroma
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataVectorStore:S5] - {error}'}

    # Loading All The Environment Value:S2
    try:
        AZURE_API_ENDPOINT = os.getenv('AZURE_API_ENDPOINT')
        AZURE_API_KEY = os.getenv('AZURE_API_KEY')
        AZURE_API_DEPLOYMENT_NAME = os.getenv('AZURE_API_DEPLOYMENT_NAME')
        AZURE_API_VERSION = os.getenv('AZURE_API_VERSION')
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataVectorStore:S2] - {error}'}

    # Validate All Environment Variables Are Present and Define Azure OpenAI Embedding Model:S4
    try:
        # Define required environment variables
        required_env_vars = {
            'AZURE_OPENAI_ENDPOINT': AZURE_API_ENDPOINT,
            'AZURE_OPENAI_API_KEY': AZURE_API_KEY,
            'AZURE_OPENAI_EMBEDDING_DEPLOYMENT': AZURE_API_DEPLOYMENT_NAME,
            'AZURE_OPENAI_API_VERSION': AZURE_API_VERSION
        }

        # Check for missing or empty environment variables
        missing_vars = []
        for var_name, var_value in required_env_vars.items():
            if var_value is None or (isinstance(var_value, str) and var_value.strip() == ''):
                missing_vars.append(var_name)

        # Return error if any required variables are missing
        if missing_vars:
            return {'status': 'ERROR', 'message': f'ERROR - [DataVectorStore:S4] - Missing Required Environment Variables: {", ".join(missing_vars)}'}
        # Define Azure OpenAI Embedding Model
        azure_embedding_object = AzureOpenAIEmbeddings(
            azure_endpoint = AZURE_API_ENDPOINT,
            api_key = AZURE_API_KEY,
            openai_api_version = AZURE_API_VERSION,
            azure_deployment = AZURE_API_DEPLOYMENT_NAME
        )
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataVectorStore:S4] - {error}'}

    # Load CSV as Documents:S5
    try:
        df = pd.read_csv(csv_file_path)
        required_cols = {'question_title', 'question_id'}
        if not required_cols.issubset(set(df.columns)):
            raise ValueError(
                f"CSV must contain columns {required_cols}, found: {list(df.columns)}"
            )
        documents = []
        for idx, row in df.iterrows():
            text_val = str(row['question_title']) if pd.notna(row['question_title']) else ""
            qid_val = row['question_id']

            doc = Document(
                page_content = text_val,
                metadata={
                    'question_id': int(qid_val) if pd.notna(qid_val) else None,
                    "row_index": int(idx),
                    "source": os.path.basename(csv_file_path),
                }
            )
            documents.append(doc)
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataVectorStore:S5] - {error}'}

    # Create Vector Store from Documents:S6
    try:
        Chroma.from_documents(
            documents = documents,
            embedding = azure_embedding_object,
            persist_directory = 'kbdb',
            collection_name = 'csv_questions',
            collection_metadata = {"hnsw:space": "cosine"}
        )
        return {'status': 'SUCCESS', 'message': 'Vector store created successfully'}
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataVectorStore:S6] - {error}'}