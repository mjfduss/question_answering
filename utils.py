class BaseLogger:
    def __init__(self) -> None:
        self.info = print


def create_vector_index(driver, dimension: int) -> None:
    index_query = """
    CALL db.index.vector.createNodeIndex('page_embeddings', 'Page', 'embedding', $dimension, 'cosine')
    """
    try:
        driver.query(index_query, {"dimension": dimension})
    except:  # Already exists
        pass