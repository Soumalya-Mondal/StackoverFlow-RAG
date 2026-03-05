# define "data_retrieval" function
def data_retrieval(query: str) -> dict:
    # Importing Python Module:S1
    try:
        import os
        from langchain_openai import AzureOpenAIEmbeddings
        from langchain_chroma import Chroma
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataRetrieval:S1] - {error}', 'documents': []}

    # Loading and Validating Environment Variables and Define Azure OpenAI Embedding Model:S2
    try:
        AZURE_API_ENDPOINT = os.getenv('AZURE_API_ENDPOINT')
        AZURE_API_KEY = os.getenv('AZURE_API_KEY')
        AZURE_API_DEPLOYMENT_NAME = os.getenv('AZURE_API_DEPLOYMENT_NAME')
        AZURE_API_VERSION = os.getenv('AZURE_API_VERSION')
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
            return {'status': 'ERROR', 'message': f'ERROR - [DataRetrieval:S2] - Missing Required Environment Variables: {", ".join(missing_vars)}', 'documents': []}
        # Define Azure OpenAI Embedding Model
        azure_embedding_object = AzureOpenAIEmbeddings(
            azure_endpoint = AZURE_API_ENDPOINT,
            api_key = AZURE_API_KEY,
            openai_api_version = AZURE_API_VERSION,
            azure_deployment = AZURE_API_DEPLOYMENT_NAME
        )
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataRetrieval:S2] - {error}', 'documents': []}

    # Load Vector Store From Persistent Directory:S3
    try:
        db = Chroma(
            persist_directory = 'kbdb',
            embedding_function = azure_embedding_object,
            collection_metadata = {"hnsw:space": "cosine"}
        )
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataRetrieval:S3] - {error}', 'documents': []}

    # Create Retriever With Similarity Score Threshold:S4
    try:
        retriever = db.as_retriever(
            search_type = "similarity_score_threshold",
            search_kwargs = {
                "k": 5,
                "score_threshold": 0.8
            }
        )
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataRetrieval:S4] - {error}', 'documents': []}

    # Retrieve Documents Based On Query:S5
    try:
        # Validate query is not empty
        if not query or (isinstance(query, str) and query.strip() == ''):
            return {'status': 'ERROR', 'message': 'ERROR - [DataRetrieval:S5] - Query Cannot Be Empty', 'documents': []}
        # Retrieve relevant documents
        relevant_docs = retriever.invoke(query)
        # Convert documents to dictionary format
        documents_list = []
        for doc in relevant_docs:
            documents_list.append({
                'content': doc.page_content,
                'metadata': doc.metadata if hasattr(doc, 'metadata') else {}
            })
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataRetrieval:S5] - {error}', 'documents': []}

    # Return Success Response With Documents:S6
    try:
        return {'status': 'SUCCESS', 'message': f'Retrieved {len(documents_list)} Relevant Documents', 'documents': documents_list}
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [DataRetrieval:S6] - {error}', 'documents': []}