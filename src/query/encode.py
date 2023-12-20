
from langchain.embeddings import VertexAIEmbeddings
from langchain.document_loaders import JSONLoader
from langchain.vectorstores import FAISS
from src.config.logging import logger
from src.config.setup import Config
from typing import List
from typing import Dict
from tqdm import tqdm


class MyVertexAIEmbeddings(VertexAIEmbeddings):
    """
    Custom class for handling batch processing with Vertex AI embeddings.
    """
    model_name = 'textembedding-gecko'
    max_batch_size = 5

    def embed_names(self, names: List[str]) -> List[List[float]]:
        """
        Embed a list of bank names using batch processing.
        
        Parameters:
        segments (List[str]): List of bank names to embed.

        Returns:
        List[List[float]]: List of embeddings for each bank name.
        """
        logger.info("Starting embedding of bank names")
        embeddings = []
        for i in tqdm(range(0, len(names), self.max_batch_size)):
            batch = names[i: i + self.max_batch_size]
            try:
                batch_embeddings = self.client.get_embeddings(batch)
                embeddings.extend(batch_embeddings)
                logger.info(f"Batch {i} embedded successfully")
            except Exception as e:
                logger.error(f"Error embedding batch {i}: {e}")
        logger.info("Completed embedding of bank names")
        return [embedding.values for embedding in embeddings]

    def embed_query(self, query: str) -> List[float]:
        """
        Embed a single query string.
        
        Parameters:
        query (str): Query string to embed.

        Returns:
        List[float]: Embedding of the query.
        """
        logger.info(f"Embedding query: {query}")
        try:
            embeddings = self.client.get_embeddings([query])
            logger.info("Query embedded successfully")
            return embeddings[0].values
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            return []

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


def execute_query(query: str, retriever):
    """
    Execute a query and log the resulting documents.
    
    Parameters:
    query (str): Query string.
    retriever: Retriever object for document retrieval.
    """
    logger.info(f"Executing query: {query}")
    try:
        banks = retriever.get_relevant_documents(query)
        for bank in banks:
            logger.info(f'Bank Name: {bank.page_content}')
            metadata = bank.metadata
            country = metadata['country']
            site_url = metadata['site_url']
            logger.info(f'Country: {country}')
            logger.info(f'Site URL: {site_url}')
            logger.info(f"\n{'-' * 100}\n")
        logger.info(f"Query executed successfully")
    except Exception as e:
        logger.error(f"Error executing query '{query}': {e}")


# Example usage
vector_store = load_and_index('./src/query/banks.jsonl')
retriever = vector_store.as_retriever(search_type='similarity', search_kwargs={'k': 3})
execute_query("islamic", retriever)
