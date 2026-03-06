# define "api_credential_check" function
def api_credential_check() -> dict:
    # Importing Python Module:S1
    try:
        import os
        from openai import AzureOpenAI
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [APICredentialCheck:S1] - {error}'}

    # Loading and Validating Environment Variables:S2
    try:
        AZURE_API_ENDPOINT = os.getenv('AZURE_API_ENDPOINT')
        AZURE_API_KEY = os.getenv('AZURE_API_KEY')
        AZURE_API_EMBEDDING_DEPLOYMENT_NAME = os.getenv('AZURE_API_EMBEDDING_DEPLOYMENT_NAME')
        AZURE_API_VERSION = os.getenv('AZURE_API_VERSION')

        # Define required environment variables
        required_env_vars = {
            'AZURE_API_ENDPOINT': AZURE_API_ENDPOINT,
            'AZURE_API_KEY': AZURE_API_KEY,
            'AZURE_API_EMBEDDING_DEPLOYMENT_NAME': AZURE_API_EMBEDDING_DEPLOYMENT_NAME,
            'AZURE_API_VERSION': AZURE_API_VERSION
        }
        # Check for missing or empty environment variables
        missing_vars = []
        for var_name, var_value in required_env_vars.items():
            if var_value is None or (isinstance(var_value, str) and var_value.strip() == ''):
                missing_vars.append(var_name)
        # Return error if any required variables are missing
        if missing_vars:
            return {'status': 'ERROR', 'message': f'ERROR - [APICredentialCheck:S2] - Missing Required Environment Variables: {", ".join(missing_vars)}'}
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [APICredentialCheck:S2] - {error}'}

    # Create Azure OpenAI Client:S3
    try:
        client = AzureOpenAI(
            api_version = AZURE_API_VERSION,
            azure_endpoint = AZURE_API_ENDPOINT,
            api_key = AZURE_API_KEY
        )
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [APICredentialCheck:S3] - {error}'}

    # Execute Embeddings Request:S4
    try:
        response = client.embeddings.create(
            input = ['first phrase', 'second phrase', 'third phrase'],
            model = AZURE_API_EMBEDDING_DEPLOYMENT_NAME
        )
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [APICredentialCheck:S4] - {error}'}

    # Validate API Response:S5
    try:
        # Check if response exists
        if response is None:
            return {'status': 'ERROR', 'message': 'ERROR - [APICredentialCheck:S5] - Response Is None'}
        # Check if response has data
        if not hasattr(response, 'data') or response.data is None:
            return {'status': 'ERROR', 'message': 'ERROR - [APICredentialCheck:S5] - Response Does Not Contain Data'}
        # Check if data list is not empty
        if len(response.data) == 0:
            return {'status': 'ERROR', 'message': 'ERROR - [APICredentialCheck:S5] - Response Data Is Empty'}
        # If all validations pass, return success
        return {'status': 'SUCCESS', 'message': 'API Credential Is Working'}
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [APICredentialCheck:S5] - {error}'}