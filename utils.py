class BaseLogger:
    def __init__(self) -> None:
        self.info = print


def create_vector_index(driver, dimension: int) -> None:
    index_query = """
    CREATE VECTOR INDEX page-embeddings
    FOR (p:Page) ON (p.embedding)
    OPTIONS {indexConfig: {
        vector.dimensions: $dimension,
        vector.similarity_function: 'cosine'
    }}
    """
    try:
        driver.query(index_query, {"dimension": dimension})
    except:  # Already exists
        pass
    index_query = """
    CREATE VECTOR INDEX subsection-embeddings
    FOR (p:Page) ON (p.child_embedding)
    OPTIONS {indexConfig: {
        vector.dimensions: $dimension,
        vector.similarity_function: 'cosine'
    }}
    """
    try:
        driver.query(index_query, {"dimension": dimension})
    except:  # Already exists
        pass