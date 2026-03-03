# define main function
if __name__ == '__main__':
    # Importing Python Module:S1
    try:
        import sys
        from pathlib import Path
    except Exception as error:
        print(f'ERROR - [Main:S1] - {error}')

    # Appending System-Path:S2
    try:
        sys.path.append(str(Path.cwd()))
        from supportscript.mergecsvfiles import merge_csv_files
    except Exception as error:
        print(f'ERROR - [Main:S2] - {error}')

    # Define Folder Path:S3
    try:
        parent_folder_path = Path.cwd()
        input_folder_path = parent_folder_path / 'input'
        output_folder_path = parent_folder_path / 'output'
    except Exception as error:
        print(f'ERROR - [Main:S3] - {error}')

    # Calling "merge_csv_files" Function:S4
    try:
        print('STEP-1 -- Merging All The CSV Files')
        merge_csv_files_backend_response = merge_csv_files(input_folder_path = str(input_folder_path), output_folder_path = str(output_folder_path))
        # Validate backend response is not empty or None
        if (merge_csv_files_backend_response is None) or (not merge_csv_files_backend_response):
            print(f'ERROR - [Main:S4] - Invalid Response From "merge_csv_files" Micro-Service Backend')
        else:
            # check the resposne from "merge_csv_files" function and print appropriate message
            if (str(merge_csv_files_backend_response['status']).upper() == 'SUCCESS'):
                if (merge_csv_files_backend_response.get('file_path') != 'N/A'):
                    print(f'STEP-1 -- {merge_csv_files_backend_response["message"]}')
                    print(f'STEP-1 -- Merged CSV File Path: {merge_csv_files_backend_response["file_path"]}')
                else:
                    print(f'ERROR - [Main:S4] - File Path Is Not Available')
            if (str(merge_csv_files_backend_response['status']).upper() == 'ERROR'):
                print(f'ERROR - [Main:S4] - {merge_csv_files_backend_response["message"]}')
    except Exception as error:
        print(f'ERROR - [Main:S4] - {error}')