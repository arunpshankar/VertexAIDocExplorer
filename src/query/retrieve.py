from src.query.embed import MyVertexAIEmbeddings
from langchain.vectorstores import FAISS
from src.config.logging import logger
from src.config.setup import Config


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


if __name__ == "__main__":
    embeddings = MyVertexAIEmbeddings()
    vector_store = FAISS.load_local("./src/query/faiss_index", embeddings)
    retriever = vector_store.as_retriever(search_type='similarity', search_kwargs={'k': 3})
    execute_query("colmbia financial SA", retriever)
