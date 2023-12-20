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