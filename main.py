from langchain_community.graphs import Neo4jGraph
from knowledgegraph import build_knowledge_graph
import bot

def main():
    print("Connecting to Neo4j Graph")
    neo4j_graph = Neo4jGraph(url="neo4j://localhost:7687", username="neo4j", password="password")

    knowledge_graph_built = build_knowledge_graph(neo4j_graph)
    print("knowledge_graph_built:", knowledge_graph_built)

    bot.startup_chatbot_api()
    
main()