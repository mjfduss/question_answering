"""
Modified from https://github.com/docker/genai-stack/blob/main/loader.py
"""
from typing import List
from langchain_community.graphs import Neo4jGraph
from chains import load_embedding_model
from utils import create_vector_index
from crawler import crawl_textbook


def insert_textbook_data(pages: List[dict], embeddings, neo4j_graph: Neo4jGraph) -> None:
    # Calculate embedding values for textbook text
    print("Building Page Embeddings")
    for page in pages:
        page['embedding'] = embeddings.embed_query(page['text'])
        #page['child_embedding'] = embeddings.embed_documents([page['title']] + page['children'])
    
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