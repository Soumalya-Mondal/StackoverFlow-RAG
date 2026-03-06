# define main function
if __name__ == '__main__':
    # Define Constant
    EMBEDDED_DATA_PRESENT_STATUS = False

    # Importing Python Module:S1
    try:
        import sys
        from pathlib import Path
        from dotenv import load_dotenv
    except Exception as error:
        print(f'ERROR - [Main:S1] - {error}')

    # Appending System-Path:S2
    try:
        sys.path.append(str(Path.cwd()))
        from supportscript.mergecsvfiles import merge_csv_files
        from supportscript.datavectorstore import data_vector_store
        from supportscript.apicredentialcheck import api_credential_check
        from supportscript.dataretrival import data_retrieval
        from supportscript.fetchquestion import fetch_question
    except Exception as error:
        print(f'ERROR - [Main:S2] - {error}')

    # Define Folder Path:S3
    try:
        parent_folder_path = Path.cwd()
        input_folder_path = parent_folder_path / 'input'
        output_folder_path = parent_folder_path / 'output'
        env_file_path = parent_folder_path / '.env'
    except Exception as error:
        print(f'ERROR - [Main:S3] - {error}')

    # Load Environment Variables From .env File:S4
    try:
        # Check if .env file exists
        if (not env_file_path.exists()):
            raise FileNotFoundError(f'.env File Not Found At {env_file_path}')
        # Load .env file and populate os.environ
        load_dotenv(dotenv_path = str(env_file_path), override = True)
    except Exception as error:
        print(f'ERROR - [Main:S4] - {error}')

    # Check If Embedded Data Already Present:S5
    try:
        chroma_db_file_path = parent_folder_path / Path('kbdb') / 'chroma.sqlite3'
        if chroma_db_file_path.exists():
            EMBEDDED_DATA_PRESENT_STATUS = True
            print('STEP-1 -- Embedded Data Already Present - Skipping Data Processing Steps')
    except Exception as error:
        print(f'ERROR - [Main:S5] - {error}')

    # Calling "merge_csv_files" Function:S6
    if not EMBEDDED_DATA_PRESENT_STATUS:
        try:
            print('STEP-2 -- Merging All The CSV Files')
            merge_csv_files_backend_response = merge_csv_files(input_folder_path = str(input_folder_path), output_folder_path = str(output_folder_path))
            # Validate backend response is not empty or None
            if (merge_csv_files_backend_response is None) or (not merge_csv_files_backend_response):
                print(f"ERROR - [Main:S6] - Invalid Response From 'merge_csv_files' Micro-Service Backend")
            else:
                # check the response from "merge_csv_files" function and print appropriate message
                if (str(merge_csv_files_backend_response['status']).upper() == 'SUCCESS'):
                    if (merge_csv_files_backend_response.get('merge_csv_file_path') != 'N/A'):
                        print(f"STEP-2 -- {merge_csv_files_backend_response['message']}")
                    else:
                        print(f"ERROR - [Main:S6] - File Path Is Not Available")
                if (str(merge_csv_files_backend_response['status']).upper() == 'ERROR'):
                    print(f"ERROR - [Main:S6] - {merge_csv_files_backend_response['message']}")
        except Exception as error:
            print(f"ERROR - [Main:S6] - {error}")

    # Calling "api_credential_check" Function:S7
    if not EMBEDDED_DATA_PRESENT_STATUS:
        try:
            print('STEP-3 -- Checking API Credentials')
            api_credential_check_backend_response = api_credential_check()
            # Validate backend response is not empty or None
            if (api_credential_check_backend_response is None) or (not api_credential_check_backend_response):
                print(f"ERROR - [Main:S7] - Invalid Response From 'api_credential_check' Micro-Service Backend")
            else:
                # check the response from "api_credential_check" function and print appropriate message
                if (str(api_credential_check_backend_response['status']).upper() == 'SUCCESS'):
                    print(f"STEP-3 -- {api_credential_check_backend_response['message']}")
                if (str(api_credential_check_backend_response['status']).upper() == 'ERROR'):
                    print(f"ERROR - [Main:S7] - {api_credential_check_backend_response['message']}")
        except Exception as error:
            print(f"ERROR - [Main:S7] - {error}")

    # Calling "data_vector_store" Function:S8
    if not EMBEDDED_DATA_PRESENT_STATUS:
        try:
            print('STEP-4 -- Creating Vector Store From CSV')
            data_vector_store_backend_response = data_vector_store(csv_file_path = str(merge_csv_files_backend_response['merge_csv_file_path']))
            # Validate backend response is not empty or None
            if (data_vector_store_backend_response is None) or (not data_vector_store_backend_response):
                print(f"ERROR - [Main:S8] - Invalid Response From 'data_vector_store' Micro-Service Backend")
            else:
                # check the response from "data_vector_store" function and print appropriate message
                if (str(data_vector_store_backend_response['status']).upper() == 'SUCCESS'):
                    print(f"STEP-4 -- {data_vector_store_backend_response['message']}")
                if (str(data_vector_store_backend_response['status']).upper() == 'ERROR'):
                    print(f"ERROR - [Main:S8] - {data_vector_store_backend_response['message']}")
        except Exception as error:
            print(f"ERROR - [Main:S8] - {error}")

    # Calling "data_retrieval" Function:S9
    try:
        query = 'How do I run Rake tasks?'
        print('STEP-5 -- Retrieving Relevant Documents')
        data_retrieval_backend_response = data_retrieval(query = query)
        # Validate backend response is not empty or None
        if (data_retrieval_backend_response is None) or (not data_retrieval_backend_response):
            print(f"ERROR - [Main:S9] - Invalid Response From 'data_retrieval' Micro-Service Backend")
        else:
            # check the response from "data_retrieval" function and print appropriate message
            if (str(data_retrieval_backend_response['status']).upper() == 'SUCCESS'):
                print(f"STEP-5 -- {data_retrieval_backend_response['message']}")
            if (str(data_retrieval_backend_response['status']).upper() == 'ERROR'):
                print(f"ERROR - [Main:S9] - {data_retrieval_backend_response['message']}")
    except Exception as error:
        print(f"ERROR - [Main:S9] - {error}")

    # Calling "fetch_question" Function:S10
    try:
        # Extract question IDs from retrieved documents
        question_id_list = []
        if (data_retrieval_backend_response is not None) and data_retrieval_backend_response.get('documents'):
            for doc in data_retrieval_backend_response['documents']:
                qid = doc.get('metadata', {}).get('question_id')
                if qid is not None:
                    question_id_list.append(qid)

        # Only proceed if we have question ids
        if question_id_list:
            print('STEP-6 -- Fetching Questions From StackOverflow')
            fetch_question_backend_response = fetch_question(question_id_list)
            if (fetch_question_backend_response is None) or (not fetch_question_backend_response):
                print(f"ERROR - [Main:S10] - Invalid Response From 'fetch_question' Micro-Service Backend")
            else:
                if (str(fetch_question_backend_response.get('status', '')).upper() == 'SUCCESS'):
                    print(f"STEP-6 -- {fetch_question_backend_response.get('message', '')}")
                    # Print all qid and qdata from the response
                    questions_data = fetch_question_backend_response.get('data', {})
                    for qid, qdata in questions_data.items():
                        print(f"\nQuestion ID: {qid}")
                        print(f"Question Data: {qdata}")
                if (str(fetch_question_backend_response.get('status', '')).upper() == 'ERROR'):
                    print(f"ERROR - [Main:S10] - {fetch_question_backend_response.get('message', '')}")
        else:
            print('STEP-6 -- No Question IDs Found In Retrieved Documents; Skipping Fetch')
    except Exception as error:
        print(f"ERROR - [Main:S10] - {error}")