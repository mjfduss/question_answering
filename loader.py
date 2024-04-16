import os
from typing import List
from dotenv import load_dotenv
from langchain.graphs import Neo4jGraph
import streamlit as st
from streamlit.logger import get_logger
from chains import load_embedding_model
from utils import create_vector_index
from PIL import Image

from crawler import crawl_textbook

load_dotenv(".env")

url = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")
ollama_base_url = os.getenv("OLLAMA_BASE_URL")
embedding_model_name = os.getenv("EMBEDDING_MODEL")
# Remapping for Langchain Neo4j integration
os.environ["NEO4J_URL"] = url

logger = get_logger(__name__)

embeddings, dimension = load_embedding_model(
    embedding_model_name, config={"ollama_base_url": ollama_base_url}, logger=logger
)

neo4j_graph = Neo4jGraph(url=url, username=username, password=password)

create_vector_index(neo4j_graph, dimension)

def load_textbook_data() -> None:
    pages = crawl_textbook()
    insert_textbook_data(pages)


def insert_textbook_data(pages: List[dict]) -> None:
    # Calculate embedding values for textbook text
    for page in pages:
        page['embedding'] = embeddings.embed_query(page['text'])
        page['child_embedding'] = embeddings.embed_documents([page['title']] + page['children'])

    # Cypher, the query language of Neo4j, is used to import the data
    # https://neo4j.com/docs/getting-started/cypher-intro/
    # https://neo4j.com/docs/cypher-cheat-sheet/5/auradb-enterprise/
    import_query = """
    UNWIND $pages AS p
    MERGE (page:Page {id:p.id})
    ON CREATE SET page.title = p.title, page.link = p.link, 
        page.text = p.text, page.embedding = p.embedding, 
        page.child_embedding = p.child_embedding
    FOREACH (c IN p.children |
        MERGE (page)-[:SUBSECTION]->(page:Page {title:c})
    )
    """
    neo4j_graph.query(import_query, {"pages": pages})


# Streamlit
def render_page():
    datamodel_image = Image.open("./images/datamodel.png")
    st.header("IR Textbook Loader")
    st.caption("Go to http://localhost:7474/ to explore the graph.")

    if st.button("Import", type="primary"):
        with st.spinner("Loading... This might take a minute or two."):
            try:
                load_textbook_data()
                st.success("Import successful", icon="✅")
                st.caption("Data model")
                st.image(datamodel_image)
                st.caption("Go to http://localhost:7474/ to interact with the database")
            except Exception as e:
                st.error(f"Error: {e}", icon="🚨")


render_page()