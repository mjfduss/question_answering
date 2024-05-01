"""
Nathan Hartzler
CSC790-SP24-Project

Modified from https://github.com/docker/genai-stack/blob/main/loader.py
and https://github.com/docker/genai-stack/blob/main/utils.py
"""
from typing import List
from langchain_community.graphs import Neo4jGraph
from chains import load_embedding_model
from crawler import crawl_textbook


def create_vector_index(driver, dimension: int) -> None:
    """Creates the vector index in the Neo4j database, if it doesn't already exist"""
    index_query = """
    CALL db.index.vector.createNodeIndex('page_embeddings', 'Page', 'embedding', $dimension, 'cosine')
    """
    try:
        driver.query(index_query, {"dimension": dimension})
    except:  # Already exists
        pass


def insert_textbook_data(pages: List[dict], embeddings, neo4j_graph: Neo4jGraph) -> None:
    """Using the list of diction objects, it calls the Neo4j database to create a new
        Page node for each page and then connects the child link pages as SubPages
        so that the relationship between different topics in the textbook are maintained
    """
    # Calculate embedding values for textbook text
    print("Building Page Embeddings")
    for page in pages:
        page['embedding'] = embeddings.embed_query(page['text'])
        # page['child_embedding'] = embeddings.embed_documents([page['title']] + page['children'])

    print("Building Knowledge Graph")
    # Cypher, the query language of Neo4j, is used to import the data
    # https://neo4j.com/docs/getting-started/cypher-intro/
    # https://neo4j.com/docs/cypher-cheat-sheet/5/auradb-enterprise/
    import_query = """
    UNWIND $pages AS p
    MERGE (page:Page {id:p.id})
    ON CREATE SET page.title = p.title, page.link = p.link, 
        page.text = p.text, page.embedding = p.embedding
    """
    neo4j_graph.query(import_query, {"pages": pages})

    subpage_query = """
    UNWIND $pages AS p
    MATCH (page:Page{id:p.id})
    UNWIND p.children AS c
    MATCH (child:Page{title:c})
    MERGE (child)-[:SUB_PAGE]->(page)
    """
    neo4j_graph.query(subpage_query, {"pages": pages})


def load_textbook_data(embeddings, neo4j: Neo4jGraph) -> None:
    """Calls the html page crawler and parser then inserts the
        pages into the database
    """
    pages = crawl_textbook()
    print("Pages crawled")
    insert_textbook_data(pages, embeddings, neo4j)


def build_knowledge_graph(neo4j_graph: Neo4jGraph):
    """Builds the Knowledge Graph in Neo4j if it doesn't already exist"""
    # Checking if Graph is empty
    count_query = """
    MATCH (p:Page)
    RETURN COUNT(p)
    """
    results = neo4j_graph.query(count_query)
    node_count = list(results[0].values())[0]

    # If graph is empty, create knowledge graph
    if not node_count > 0:

        print("Loading Embedding Model")
        embeddings, dimension = load_embedding_model()
        create_vector_index(neo4j_graph, dimension)

        try:
            load_textbook_data(embeddings, neo4j_graph)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    # If graph is not empty, do nothing
    return True


def setup():
    """Connects to the local Neo4j database and checks if the 
        knowledge graph is built already
    """
    print("Connecting to Neo4j Graph")
    neo4j_graph = Neo4jGraph(
        url="neo4j://localhost:7687", username="neo4j", password="password")

    knowledge_graph_built = build_knowledge_graph(neo4j_graph)
    print("knowledge_graph_built:", knowledge_graph_built)
