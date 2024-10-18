from DataCleaningAgent.tools.ocrmypdf import OCRMyPDF
from langchain.agents import Tool

# from DataCleaningAgent.behaviours.PDFCleaning import PDFCleaning

class PDFCleaning():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_pdf(self, pdf_path):
        OCRMyPDF().ocr_directory(pdf_path)

    def detect_named_entities(self, text_files):
        # Detect all named entities in text_files
        # double check the output of this function
        # for correctness and recommend changes
        pass

    def detect_topics(self, text_files):
        # Detect all topics in text_files
        # double check the output of this function
        pass

    def clean_errors(self, text_files):
        # Clean all errors in text_files
        # double check the output of this function
        pass

    def tool_factory(self):
        return [Tool(
            name="ocrmypdf",
            func=self.clean_pdf,
            description="""
            accepts a full path to a directory of PDFs
            used for cleaning a directory of PDFs
            uses ocrmypdf to generate text from PDFs
            """
        )]