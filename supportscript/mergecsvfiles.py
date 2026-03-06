# define "merge_csv_files" function
def merge_csv_files(input_folder_path: str, output_folder_path: str) -> dict:
    # Importing Python Module:S1
    try:
        from pathlib import Path
        import pandas
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [MergeCSVFiles:S1] - {error}', 'merge_csv_file_path': 'N/A'}

    # Fetch All CSV Files From Input Folder:S2
    try:
        input_folder_path_object = Path(input_folder_path)
        # Check if input folder exists
        if (not input_folder_path_object.exists()):
            return {'status': 'ERROR', 'message': 'ERROR - [MergeCSVFiles:S2] - Input Folder Does Not Exist', 'merge_csv_file_path': 'N/A'}
        # Recursively collect all .csv files from input folder and subdirectories
        csv_files_list = list(input_folder_path_object.rglob('*.csv'))
        if (not csv_files_list):
            return {'status': 'ERROR', 'message': 'ERROR - [MergeCSVFiles:S2] - No CSV Files Found', 'merge_csv_file_path': 'N/A'}
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [MergeCSVFiles:S2] - {error}', 'merge_csv_file_path': 'N/A'}

    # Read CSV Files And Extract Required Columns:S3
    try:
        # Read only required columns from CSV files
        required_columns = ["Question_ID", "Question_Title"]
        combined_dataframes = []
        for csv_file in csv_files_list:
            try:
                csv_file_dataframe = pandas.read_csv(csv_file, usecols = required_columns)
                # Rename columns to lowercase with underscores
                csv_file_dataframe = csv_file_dataframe.rename(columns = {'Question_ID': 'question_id', 'Question_Title': 'question_title'})
                # Reorder columns: "question_title" first, then "question_id"
                csv_file_dataframe = csv_file_dataframe[["question_title", "question_id"]]
                combined_dataframes.append(csv_file_dataframe)
            except KeyError:
                return {'status': 'ERROR', 'message': f'ERROR - [MergeCSVFiles:S3] - Missing Required Columns In File: {csv_file.name}', 'merge_csv_file_path': 'N/A'}
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [MergeCSVFiles:S3] - {error}', 'merge_csv_file_path': 'N/A'}

    # Merge CSV Dataframes Into Single Dataframe:S4
    try:
        # Concatenate all "combined_dataframes"
        merged_final_dataframe = pandas.concat(combined_dataframes, ignore_index = True)
        # Delete "combined_dataframes" to save memory
        del combined_dataframes
        # Remove duplicate rows based on "question_id" and "question_title"
        merged_final_dataframe = merged_final_dataframe.drop_duplicates(subset = ['question_id', 'question_title'], keep = 'first')
        # Sort by "question_id" in ascending order
        merged_final_dataframe = merged_final_dataframe.sort_values(by = 'question_id', ascending = True)
        # Reset index after sorting
        merged_final_dataframe = merged_final_dataframe.reset_index(drop = True)
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [MergeCSVFiles:S4] - {error}', 'merge_csv_file_path': 'N/A'}

    # Save Merged Dataframe To "output" Folder:S5
    try:
        output_folder_path_object = Path(output_folder_path)
        # Define output file path
        output_file = output_folder_path_object / 'stackoverflowdata.csv'
        # Get absolute path of the output file
        output_file_absolute_path = output_file.resolve()
        # Delete existing file if it exists
        if output_file.exists():
            output_file.unlink()
        # Save merged file
        merged_final_dataframe.to_csv(output_file, index = False)
        # Delete "merged_final_dataframe" to save memory
        del merged_final_dataframe
        return {'status': 'SUCCESS', 'message': f'Successfully Merged {len(csv_files_list)} CSV Files', 'merge_csv_file_path': str(output_file_absolute_path)}
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [MergeCSVFiles:S5] - {error}', 'merge_csv_file_path': 'N/A'}