"""
Nathan Hartzler
CSC790-SP24-Project

Modified from https://github.com/docker/genai-stack/blob/main/chains.py
"""
from langchain_community.embeddings import (
    SentenceTransformerEmbeddings,
)
from langchain_community.chat_models import ChatOllama
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


def load_embedding_model():
    """Returns the pretrained sentence text embedder model
        Will download the model from HuggingFace if it is not already
        cached in the local "embedding_model" folder
    """
    embeddings = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2", cache_folder="embedding_model"
    )
    dimension = 384
    return embeddings, dimension


def load_llm():
    """Calls the local ollama server on localhost:11434 and loads the default llama2 LLM"""
    return ChatOllama(
        temperature=0,
        streaming=True,
        # seed=2,
        # A higher value (100) will give more diverse answers, while a lower value (10) will be more conservative.
        top_k=10,
        # Higher value (0.95) will lead to more diverse text, while a lower value (0.5) will generate more focused text.
        top_p=0.3,
        # Sets the size of the context window used to generate the next token.
        num_ctx=3072,
    )


def configure_qa_kg_chain(llm, embeddings, neo4jurl="neo4j://localhost:7687", username="neo4j", password="password"):
    """Creates the database connection to the Neo4j server and sets up the 'glue' between the 
        Neo4j knowlegde graph and the ollama LLM
    """
    # Response
    general_system_template = """ 
    Use the following pieces of context to answer question at the end.
    The context contains pages and their links from the Introduction to Information Retrieval textbook.
    When you find a particular segment of text in in the context useful, make sure to cite it in the answer using the page link.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    ----
    {summaries}
    ----
    Each answer you generate should contain a section at the end of links to 
    the textbook pages you found useful, which are described under Source value.
    You can only use links to the pages that are present in the context and always
    add links to the end of the answer in the style of citations.
    Generate concise answers with references sources section of links to 
    relevant page text only at the end of the answer.
    """
    general_user_template = "Question:```{question}```"
    messages = [
        SystemMessagePromptTemplate.from_template(general_system_template),
        HumanMessagePromptTemplate.from_template(general_user_template),
    ]
    qa_prompt = ChatPromptTemplate.from_messages(messages)

    qa_chain = load_qa_with_sources_chain(
        llm,
        chain_type="stuff",
        prompt=qa_prompt,
    )

    # Vector + Knowledge Graph response
    kg = Neo4jVector.from_existing_index(
        embedding=embeddings,
        url=neo4jurl,
        username=username,
        password=password,
        database="neo4j",
        index_name="page_embeddings",
        text_node_property="text",
        retrieval_query="""
        WITH node AS page, score AS similarity
        RETURN '##Page: ' + page.title + '\n' + page.text AS text, similarity as score, {source: page.link} AS metadata
        """
    )

    kg_qa = RetrievalQAWithSourcesChain(
        combine_documents_chain=qa_chain,
        retriever=kg.as_retriever(search_kwargs={"k": 2}),
        reduce_k_below_max_tokens=False,
        max_tokens_limit=3375,
    )
    return kg_qa
