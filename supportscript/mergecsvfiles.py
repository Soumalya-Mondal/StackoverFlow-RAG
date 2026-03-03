# define "merge_csv_files" function
def merge_csv_files(input_folder_path: str, output_folder_path: str) -> dict[str, str]:
    # Importing Python Module:S1
    try:
        from pathlib import Path
        import pandas
        from tqdm import tqdm
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [MergeCSVFiles:S1] - {error}'}

    # Fetch All CSV Files From Input Folder:S2
    try:
        input_folder_path_object = Path(input_folder_path)
        # Check if input folder exists
        if (not input_folder_path_object.exists()):
            return {'status': 'ERROR', 'message': 'ERROR - [MergeCSVFiles:S2] - Input Folder Does Not Exist'}
        # Recursively collect all .csv files from input folder and subdirectories
        csv_files_list = list(input_folder_path_object.rglob('*.csv'))
        if (not csv_files_list):
            return {'status': 'ERROR', 'message': 'ERROR - [MergeCSVFiles:S2] - No CSV Files Found'}
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [MergeCSVFiles:S2] - {error}'}

    # Read CSV Files And Extract Required Columns:S3
    try:
        # Read only required columns from CSV files
        required_columns = ["Question_ID", "Question_Title"]
        combined_dataframes = []
        for csv_file in tqdm(csv_files_list, desc="Reading CSV Files", bar_format='{desc}: {percentage:.0f}%|{bar}| {n_fmt}/{total_fmt}'):
            try:
                csv_file_dataframe = pandas.read_csv(csv_file, usecols = required_columns)
                # Rename columns to lowercase with underscores
                csv_file_dataframe = csv_file_dataframe.rename(columns = {"Question_ID": "question_id", "Question_Title": "question_title"})
                # Reorder columns: "question_id" first, then "question_title"
                csv_file_dataframe = csv_file_dataframe[["question_id", "question_title"]]
                combined_dataframes.append(csv_file_dataframe)
            except KeyError:
                return {'status': 'ERROR', 'message': f'ERROR - [MergeCSVFiles:S3] - Missing Required Columns In File: {csv_file.name}'}
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [MergeCSVFiles:S3] - {error}'}

    # Merge CSV Dataframes Into Single Dataframe:S4
    try:
        # Concatenate all "combined_dataframes"
        merged_final_dataframe = pandas.concat(combined_dataframes, ignore_index = True)
        # Delete "combined_dataframes" to save memory
        del combined_dataframes
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [MergeCSVFiles:S4] - {error}'}

    # Save Merged Dataframe To "output" Folder:S5
    try:
        output_folder_path_object = Path(output_folder_path)
        # Define output file path
        output_file = output_folder_path_object / 'stackoverflowdata.csv'
        # Delete existing file if it exists
        if output_file.exists():
            output_file.unlink()
        # Save merged file
        merged_final_dataframe.to_csv(output_file, index = False)
        # Delete "merged_final_dataframe" to save memory
        del merged_final_dataframe
        return {'status': 'SUCCESS', 'message': f'Successfully Merged {len(csv_files_list)} CSV files'}
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [MergeCSVFiles:S5] - {error}'}