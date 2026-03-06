# StackoverFlow-RAG

This project is a Retrieval-Augmented Generation (RAG) system designed to work with Stack Overflow data. It processes CSV files containing Stack Overflow questions, creates a searchable vector store, and retrieves relevant question data from Stack Overflow based on a user's query.

## Features

- **CSV Merging**: Combines multiple CSV files into a single, cleaned dataset.
- **Vector Store Creation**: Builds a ChromaDB vector store from question titles using Azure OpenAI embeddings for efficient similarity search.
- **Data Retrieval**: Fetches relevant document snippets from the vector store based on a natural language query.
- **Stack Overflow Integration**: Retrieves full question details from Stack Overflow using the question IDs found during retrieval.
- **Credential Validation**: Checks Azure OpenAI API credentials before making calls.
- **Modular Design**: The project is broken down into distinct Python scripts for each major function (merging, vectorizing, retrieving, etc.).

## Project Structure

```
.
├── input/                  # Directory for raw input CSV files
├── output/                 # Directory for the merged CSV file
├── kbdb/                   # Directory for the ChromaDB vector store
├── supportscript/          # Contains all the core Python modules
│   ├── apicredentialcheck.py
│   ├── dataretrival.py
│   ├── datavectorstore.py
│   ├── fetchquestion.py
│   └── mergecsvfiles.py
├── main.py                 # Main script to run the entire pipeline
├── pyproject.toml          # Project dependencies and metadata
├── README.md               # This file
└── .env                    # Configuration file for API keys (not included in repo)
```

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Soumalya-Mondal/StackoverFlow-RAG.git
    cd StackoverFlow-RAG
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You will need to create a `requirements.txt` file from `pyproject.toml` or install dependencies manually)*

## Configuration

Before running the application, you need to set up your Azure OpenAI credentials.

1.  Create a file named `.env` in the root directory of the project.
2.  Add the following environment variables to the `.env` file with your specific credentials:

    ```env
    AZURE_API_ENDPOINT="<YOUR_AZURE_API_ENDPOINT>"
    AZURE_API_KEY="<YOUR_AZURE_API_KEY>"
    AZURE_API_EMBEDDING_DEPLOYMENT_NAME="<YOUR_EMBEDDING_DEPLOYMENT_NAME>"
    AZURE_API_VERSION="<YOUR_API_VERSION>"
    ```

## Usage

To run the entire data processing and retrieval pipeline, execute the `main.py` script from the root directory:

```bash
python main.py
```

The script will perform the following steps:
1.  Merge all CSV files from the `input` directory.
2.  Check the provided Azure OpenAI API credentials.
3.  Create a vector store in the `kbdb` directory.
4.  Perform a sample data retrieval for the query "How to set up a CSS switcher?".
5.  Fetch the full question details from Stack Overflow for the retrieved results.

If a vector store already exists in the `kbdb` directory, the script will skip the data processing steps (merging, credential check, and vector store creation) and proceed directly to data retrieval.

## Dependencies

The project relies on the following Python libraries:

- `beautifulsoup4`
- `chromadb`
- `langchain-chroma`
- `langchain-community`
- `langchain-core`
- `langchain-openai`
- `langchain-text-splitters`
- `lxml`
- `pandas`
- `python-dotenv`
- `requests`

These are listed in the `pyproject.toml` file.
