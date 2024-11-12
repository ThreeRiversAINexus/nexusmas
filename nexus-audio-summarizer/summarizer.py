import os
import re
import sys
from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.mapreduce import MapReduceChain
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import AnalyzeDocumentChain

llm = OpenAI(temperature=0)
text_splitter = CharacterTextSplitter()

chain = load_summarize_chain(llm, chain_type="map_reduce")

def build_documents(directory_path, combined_file_path):
        # A regex pattern to match the filenames, the first group is optional
    file_pattern = re.compile(r"(\d+)?_audio_(\d+)\.txt$")

    txt_files = []

    for filename in os.listdir(directory_path):
        if file_pattern.search(filename):
            match = file_pattern.search(filename)
            example_number = int(match.group(1)) if match.group(1) else 0
            audio_number = int(match.group(2))
            txt_files.append((example_number, audio_number, filename))

    # Sorting files by their numerical prefix (if it exists) and suffix
    txt_files.sort()

    # # If you just need the sorted filenames, you can do this
    sorted_filenames = [filename for _, _, filename in txt_files]
    
    combined_text = ""  # This will hold the combined text from all files

    for txt_file in sorted_filenames:
        print(f"Processing file: {txt_file}")
        file_path = os.path.join(directory_path, txt_file)
        
        with open(file_path) as f:
            file_content = f.read()
        
        combined_text += "\n" + file_content

    print("Finished combining all files")

    # Write the combined text to a new file
    with open(combined_file_path, 'w') as f:
        f.write(combined_text)

    print(f"Combined text written to file: {combined_file_path}")

    texts = text_splitter.split_text(combined_text)
    docs = [Document(page_content=t) for t in texts]

    return docs

def summarize_documents(combined_file_path):
    # Running the chain
    print("Running the chain for all documents")
    with open(combined_file_path) as f:
        combined_text = f.read()
    summarize_document_chain = AnalyzeDocumentChain(combine_docs_chain=chain)
    output = summarize_document_chain.run(combined_text)
    print("Finished processing all documents")

    return output

# The path to the directory to be processed
combined_file_path = sys.argv[1]
directory_path = sys.argv[2]
# The path where the combined text will be written
docs = build_documents(directory_path, combined_file_path)
summary = summarize_documents(combined_file_path)
print(summary)
