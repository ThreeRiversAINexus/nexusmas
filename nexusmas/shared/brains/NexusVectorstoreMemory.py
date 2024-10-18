import os
from langchain.memory import VectorStoreRetrieverMemory
from typing import Optional
import faiss
from langchain.docstore import InMemoryDocstore
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import VectorStoreRetrieverMemory
import asyncio
from typing import Any, Dict, Optional
class NexusVectorstoreMemory(VectorStoreRetrieverMemory):
    vectorstore: Optional[FAISS]=None
    index_name: str = None

    def __init__(self, *args, **kwargs):
        memory_count = kwargs.pop("memory_count", 2)
        embedding_size = 1536 # Dimensions of the OpenAIEmbeddings
        index = faiss.IndexFlatL2(embedding_size)
        embedding_fn = OpenAIEmbeddings().embed_query
        # This might leave off the last message?
        in_memory_docstore = InMemoryDocstore({})
        vectorstore = None
        index_name=kwargs.pop("index_name", os.environ.get("NEXUS_AGENT_JID", None))
        vectorstore_path = self.get_vectorstore_path(index_name)
        if (not os.path.exists(vectorstore_path)):
            vectorstore = FAISS(embedding_fn, index, in_memory_docstore, {})
            vectorstore.save_local(vectorstore_path, index_name)
            print("Loaded vectorstore from local")
        else:
            vectorstore = FAISS.load_local(vectorstore_path, index_name=index_name, embeddings=OpenAIEmbeddings())

        retriever = vectorstore.as_retriever()
        retriever.search_kwargs['k'] = memory_count
        retriever.search_kwargs['fetch_k'] = 20
        super().__init__(memory_key="long_term_memory", retriever=retriever, input_key="input", *args, **kwargs)
        # I need to change this to use the sender_str
        self.index_name=index_name
        self.vectorstore=vectorstore

    # I need to change this to use the current user's
    # 'my_jabber_id' instead of index_name as the path
    def get_vectorstore_path(self, index_name):
        return "nexus_vectorstore_memory_local/" + index_name

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        # super().save_context(*args, **kwargs)
        """Save context from this conversation to buffer."""
        from pprint import pprint
        print("nexusvectorstorememory save_context")
        pprint(inputs)
        pprint(outputs)
        inputs_to_save = {}
        inputs_to_save["input"] = inputs["input"]
        documents = self._form_documents(inputs_to_save, outputs)
        self.retriever.add_documents(documents)
        asyncio.create_task(self.save_context_async())

    async def save_context_async(self, *args, **kwargs):
        self.vectorstore.save_local(self.get_vectorstore_path(self.index_name), self.index_name)