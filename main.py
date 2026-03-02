# define main function
if __name__ == '__main__':
    # Importing Python Module:S1
    try:
        from pathlib import Path
    except Exception as error:
        print(f'ERROR - [Main:S1] - {error}')

    # Define Folder Path:S2
    try:
        parent_folder_path = Path.cwd()
        input_folder_path = parent_folder_path / 'input'
    except Exception as error:
        print(f'ERROR - [Main:S2] - {error}')