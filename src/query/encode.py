from langchain.document_loaders import JSONLoader
from src.query.embed import MyVertexAIEmbeddings
from langchain.vectorstores import FAISS
from src.config.logging import logger
from src.config.setup import Config

from typing import List
from typing import Dict
from tqdm import tqdm


def extract_metadata(record: Dict, metadata: Dict) -> Dict:
    """
    Extract necessary metadata from a record.
    
    Parameters:
    record (Dict): Record from which to extract metadata.
    metadata (Dict): Metadata dictionary to update.

    Returns:
    Dict: Updated metadata dictionary.
    """
    metadata['country'] = record.get('country', 'Unknown')
    metadata['site_url'] = record.get('site_url', 'Unknown')
    return metadata


def load_and_index(file_path: str) -> FAISS:
    """
    Load data from JSONL file and index them in a FAISS vector store.
    
    Parameters:
    file_path (str): Path to the JSONL file.

    Returns:
    FAISS: FAISS vector store with loaded data.
    """
    logger.info(f"Starting to load data from {file_path}")

    try:
        loader = JSONLoader(file_path=file_path,
                            jq_schema='.',
                            metadata_func=extract_metadata,
                            content_key='bank_name',
                            json_lines=True)
        segments = loader.load()
        logger.info("Data loaded successfully")

        logger.info("Initializing text embedder")
        text_embedder = MyVertexAIEmbeddings()
        logger.info("Text embedder initialized")

        logger.info("Creating FAISS vector store from loaded data")
        vector_store = FAISS.from_documents(segments, text_embedder)
        logger.info("FAISS vector store created successfully")

        return vector_store
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")


if __name__ == "__main__":
    vector_store = load_and_index("./src/query/banks_all.jsonl")
    vector_store.save_local("./src/query/faiss_index")