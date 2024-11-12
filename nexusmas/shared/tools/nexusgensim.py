from langchain.agents import Tool
from gensim import corpora
from gensim.models import LdaModel
from gensim.parsing.preprocessing import preprocess_string, strip_tags, strip_punctuation, strip_multiple_whitespaces, strip_numeric, remove_stopwords, strip_short
from shared.tools.shared import NexusTool

# Define custom filters to preprocess the text
CUSTOM_FILTERS = [lambda x: x.lower(), strip_tags, strip_punctuation, strip_multiple_whitespaces, strip_numeric, remove_stopwords, strip_short]

class NexusGensim(NexusTool):
    def __init__(self):
        self.dictionary = None
        self.corpus = None
        self.lda_model = None

    def tool_factory(self):
        return [Tool(
            name="gensim_topics",
            func=self.find_topics,
            description="""
            accepts a chunk of text to find the list
            of topics in the text using gensim
            """
        )]

    def find_topics(self, text):
        self.preprocess(text)
        self.run_lda()
        return self.get_dominant_topic_terms()

    def preprocess(self, text):
        """Preprocess the text and update dictionary and corpus."""
        # Tokenize and preprocess the text
        tokens = preprocess_string(text, filters=CUSTOM_FILTERS)
        
        # Create dictionary and corpus
        if not self.dictionary:
            self.dictionary = corpora.Dictionary([tokens])
            self.corpus = [self.dictionary.doc2bow(tokens)]
        else:
            self.dictionary.add_documents([tokens])
            self.corpus.append(self.dictionary.doc2bow(tokens))

    def run_lda(self, num_topics=5, passes=15):
        """Run LDA on the preprocessed corpus."""
        if not self.corpus:
            raise ValueError("You need to preprocess text first.")
        
        self.lda_model = LdaModel(self.corpus, num_topics=num_topics, id2word=self.dictionary, passes=passes)

    def print_topics(self):
        """Print the topics derived from LDA."""
        if not self.lda_model:
            raise ValueError("You need to run LDA first.")
        
        topics = self.lda_model.print_topics()
        for topic in topics:
            print(topic)

    def get_dominant_topic(self):
        for index, doc_bow in enumerate(self.corpus):
            topics = self.lda_model.get_document_topics(doc_bow)
            dominant_topic = max(topics, key=lambda x: x[1])  # Get topic with max proportion
            print(f"Document {index} has dominant topic {dominant_topic[0]} with proportion {dominant_topic[1]:.4f}")
            return dominant_topic[0]
        
    def get_dominant_topic_terms(self):
        dominant_topic = self.get_dominant_topic()
        # Get the terms associated with the dominant topic
        topic_terms = self.lda_model.show_topic(dominant_topic)
        
        # Extract only the terms without their probabilities
        terms = [term for term, prob in topic_terms]
        
        return terms


## Example usage:
#text_chunk = "Gensim is a powerful library for topic modeling. It is used in many natural language processing tasks. Gensim is especially popular for its Latent Dirichlet Allocation implementation."
#
#nexus = NexusGensim()
#nexus.preprocess(text_chunk)
#nexus.run_lda(num_topics=3)
#nexus.print_topics()
#print(nexus.get_dominant_topic_terms())