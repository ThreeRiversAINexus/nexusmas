from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import DeepLake
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain

class NexusVectorstoreUnderstanding():
    def __init__(self, *args, **kwargs):
        self.dataset_path = None
        super().__init__(*args, **kwargs)

    def load_deeplake(self, dataset_path):
        if not dataset_path:
            raise Exception("dataset_path is required")
        self.dataset_path = dataset_path
        embeddings = OpenAIEmbeddings(disallowed_special=())
        self.db[self.dataset_path] = DeepLake(dataset_path=self.dataset_path, embedding_function=embeddings, read_only=True)

    def deeplake_retriever(self, dataset_path):
        retriever = self.db[dataset_path].as_retriever()

        retriever.search_kwargs['distance_metric'] = 'cos'
        retriever.search_kwargs['fetch_k'] = 20
        retriever.search_kwargs['maximal_marginal_relevance'] = True
        retriever.search_kwargs['k'] = 5 

        return retriever

    def load_chroma(self, dataset_path):
        if not dataset_path:
            raise Exception("dataset_path is required")

        self.dataset_path = dataset_path

        embeddings = OpenAIEmbeddings(disallowed_special=())

        self.db[self.dataset_path] = Chroma(dataset_path=self.dataset_path, embedding_function=embeddings, read_only=True)

        docsearch = Chroma(persist_directory="chroma/" + dataset_path, 
        embedding_function=embeddings)

        self.db[self.dataset_path] = docsearch

    def chroma_retriever(self, dataset_path):
        retriever = self.db[dataset_path].as_retriever()

        return retriever