from langchain.tools import StructuredTool
from langchain.chains.mapreduce import MapReduceChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ReduceDocumentsChain, MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.document_loaders import TextLoader

from shared.database.NexusDatabase import NexusDatabase

import os
import hashlib

class FileSummarizer():
    def calculate_checksum(self, filepath):
        """Accepts 1 arg, a filepath.
        Calculates the checksum of the file and returns it."""
        
        # Using SHA256 for the checksum
        sha256 = hashlib.sha256()
        
        # Ensure the file exists
        if not os.path.isfile(filepath):
            return "The specified file does not exist."

        # Open the file in binary read mode
        with open(filepath, 'rb') as f:
            # Read the file in chunks to compute its checksum
            for chunk in iter(lambda: f.read(4096), b''):  # reading in 4K chunks
                sha256.update(chunk)
        
        return sha256.hexdigest()

    def summarize(self, filepath):
        """Accepts 1 args, a filepath.
        Summarizes the file and returns a summary of the main themes of the file"""

        # Implement caching for the file summary here
        # we will store the cached summary in our pg database
        # if the file matches a checksum, return the cached summary
        # otherwise, summarize the file and cache the summary
        # calculate checksum

        try:
            loader = TextLoader(filepath)
            docs = loader.load()
            nd = NexusDatabase()
            checksum = self.calculate_checksum(filepath)
            summary = nd.get_summary_by_checksum(checksum)
            if summary is not None:
                return self.wrap_summary_output(summary)
        except Exception as e:
            print(e)
            return "Sorry, I had an issue while reading the file: {e}".format(e=e)

        llm = ChatOpenAI(temperature=0)

        # Map
        map_template = """The following is a set of documents
        {docs}
        Based on this list of docs, please summarize them.
        Helpful Answer:"""
        map_prompt = PromptTemplate.from_template(map_template)
        map_chain = LLMChain(llm=llm, prompt=map_prompt)
        # langchain summarization here

        # Reduce
        reduce_template = """The following is set of summaries:
        {doc_summaries}
        Take these and distill it into a final, consolidated summary of the content. 
        Helpful Answer:"""
        reduce_prompt = PromptTemplate.from_template(reduce_template)

        # Run chain
        reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

        # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain, document_variable_name="doc_summaries"
        )

        # Combines and iteravely reduces the mapped documents
        reduce_documents_chain = ReduceDocumentsChain(
            # This is final chain that is called.
            combine_documents_chain=combine_documents_chain,
            # If documents exceed context for `StuffDocumentsChain`
            collapse_documents_chain=combine_documents_chain,
            # The maximum number of tokens to group documents into.
            token_max=4000,
        )

        # Combining documents by mapping a chain over them, then combining results
        map_reduce_chain = MapReduceDocumentsChain(
            # Map chain
            llm_chain=map_chain,
            # Reduce chain
            reduce_documents_chain=reduce_documents_chain,
            # The variable name in the llm_chain to put the documents in
            document_variable_name="docs",
            # Return the results of the map steps in the output
            return_intermediate_steps=False,
        )

        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1000, chunk_overlap=0
        )
        split_docs = text_splitter.split_documents(docs)
        summary = map_reduce_chain.run(split_docs)
        nd.insert_summary(source_location=filepath, source_checksum=checksum, summary=summary)
        return self.wrap_summary_output(summary)

    def wrap_summary_output(self, summary):
        """Accepts 1 arg, a summary.
        Wraps the summary in a message and returns it."""
        return """The complete summary is: {summary}""".format(summary=summary)

    def tool_factory(self):
        tool = StructuredTool.from_function(self.summarize)
        return tool
