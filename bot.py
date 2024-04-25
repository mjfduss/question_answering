from langchain.callbacks.base import BaseCallbackHandler
from chains import (
    load_embedding_model,
    load_llm,
    configure_qa_kg_chain
)

def startup_chatbot_api():

    embeddings, dimension = load_embedding_model()

    class StreamHandler(BaseCallbackHandler):
        def __init__(self, container, initial_text=""):
            self.container = container
            self.text = initial_text

        def on_llm_new_token(self, token: str, **kwargs) -> None:
            self.text += token
            self.container.markdown(self.text)


    llm = load_llm()
    kg_chain = configure_qa_kg_chain(llm, embeddings)