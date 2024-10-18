from spade.behaviour import OneShotBehaviour
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import DeepLake
import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
import shutil
import re


from shared.behaviours.Replying import Replying

from abc import ABC, abstractmethod

class DataLoader(ABC):
    @abstractmethod
    def load_data(self):
        pass

class GithubLoader(DataLoader):
    def __init__(self, repo_name, repo_url):
        self.repo_name = repo_name
        self.repo_url = repo_url

    def load_data(self):
        data_lake_path = 'nexus-data-lake'
        if not os.path.exists(self.repo_name):
            result = os.system(f"git clone {self.repo_url} {data_lake_path}/{self.repo_name}")
            if result != 0:
                print(f"Failed to clone repository: {self.repo_url}")
                return
        else:
            print(f"Repository {self.repo_name} already exists. Skipping clone operation.")
        return './' + data_lake_path + '/' + self.repo_name

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFLoader

class PDFLoader(DataLoader):
    def __init__(self, full_path, chroma_path, **kwargs):
        self.full_path = full_path
        self.chroma_path = chroma_path
        self.overwrite = kwargs.get('overwrite', False)

    def load_data(self):
        # Make sure the chroma_path does not exist
        # Also make sure we secure the PDF original
        # And if it was sent directly to the agent, we need to move it to the data lake
        # Additionally we should accept a URL to a PDF
        print(f"full_path: {self.full_path}")
        print(f"chroma_path: {self.chroma_path}")
        if (not os.path.isdir(self.chroma_path)) or self.overwrite:
            os.mkdir(self.chroma_path)
            # Create .gitignore file
            with open(self.chroma_path + "/.gitignore", "w") as f:
                f.write("*")
            # loader = PyPDFLoader(self.full_path)
            # documents = loader.load()
            # text_splitter = CharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            # docs = text_splitter.split_documents(documents)
            # embedding = OpenAIEmbeddings()
            # vectordb = Chroma.from_documents(documents=docs, embedding=embedding, persist_directory=self.chroma_path)
            # vectordb.persist()
        if not os.path.exists(self.full_path):
            print(f"File {self.full_path} does not exist.")
            return
        return self.full_path

class DataReader(ABC):
    @abstractmethod
    def read_data(self, path):
        pass

class PDFReader(DataReader):
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def read_data(self, path):
        loader = PyPDFLoader(path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        docs = text_splitter.split_documents(documents)
        return docs


class PlainTextReader(DataReader):
    def read_data(self, path):
        docs = []
        for dirpath, dirnames, filenames in os.walk(path):
            for file in filenames:
                try: 
                    loader = TextLoader(os.path.join(dirpath, file), encoding='utf-8')
                    docs.extend(loader.load_and_split())
                except Exception as e: 
                    print(f"Failed to load and split file: {file}. Exception: {e}")
                    continue
        return docs

class DataEmbedding(ABC):
    @abstractmethod
    def embed_data(self, docs):
        pass

class OpenAIEmbeddingsEmbedder(DataEmbedding):
    def embed_data(self, docs):
        chunk_size = 500
        chunk_overlap = 50
        text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        texts = text_splitter.split_documents(docs)
        return texts
    def get_embedder(self):
        return OpenAIEmbeddings(disallowed_special=())

class VectorstoreWriter(ABC):
    @abstractmethod
    def write_to_vectorstore(self, docs):
        pass

class DeepLakeWriter(VectorstoreWriter):
    def __init__(self, username, repo_name):
        self.username = username
        self.repo_name = repo_name

    def write_to_vectorstore(self, docs, success_callback=None):
        if not self.username: 
            print("Username is not set. Please set your username from app.activeloop.ai")
            return
        try:
            embedder = OpenAIEmbeddingsEmbedder().get_embedder()
            db = DeepLake(dataset_path=f"hub://{self.username}/{self.repo_name}", embedding_function=embedder)
            db.add_documents(docs)
            if success_callback is not None:
                success_callback(username, repo_name)
        except Exception as e:
            print(f"Failed to add documents to DeepLake. Exception: {e}")
            return

class ChromaWriter(VectorstoreWriter):
    def __init__(self, chroma_path):
        self.persist_directory = chroma_path

    def write_to_vectorstore(self, docs):
        embedding = OpenAIEmbeddings()
        vectordb = Chroma.from_documents(documents=docs, embedding=embedding, persist_directory=self.persist_directory)
        vectordb.persist()

class VectorstorePopulating(OneShotBehaviour):
    def __init__(self, data_loader, data_reader, data_embedder, vectorstore_writer, callback=None):
        self.data_loader = data_loader
        self.data_reader = data_reader
        self.data_embedder = data_embedder
        self.vectorstore_writer = vectorstore_writer
        if callback is not None:
            self.callback = callback
        super().__init__()

    async def run(self):
        print("Here is where we will populate the vectorstore.")
        response = "I tried."
        try:
            path = self.data_loader.load_data()
            docs = self.data_reader.read_data(path)
            embedded_docs = self.data_embedder.embed_data(docs)
            self.vectorstore_writer.write_to_vectorstore(embedded_docs)
            response = "Successfully populated the vectorstore."
            print(response)
        except Exception as e:
            response = f"Failed to populate the vectorstore. Exception: {e}"
            print(response)

        if self.callback is not None:
            self.callback(response)
