from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.llms import GPT4All  

class NexusLLMFactory():
    def __init__(self):
        #self.openai_model = 'gpt-3.5-turbo-0301'
        # self.openai_model = 'davinci'
        self.openai_model = 'text-davinci-003'
        self.chat_openai_model = 'gpt-3.5-turbo-16k'

    def create_llm(self, temperature=0.1, max_tokens=2000):
        return OpenAI(model=self.openai_model, temperature=temperature, max_tokens=max_tokens, verbose=True)
    
    def create_chat_llm(self, temperature=0.9, max_tokens=1000, **kwargs):
        model_name = kwargs.pop("model_name", self.chat_openai_model)
        print("model_name", model_name)
        return ChatOpenAI(model=model_name, temperature=temperature, max_tokens=max_tokens, verbose=True)
    
    def create_local_llm(self):
        n_ctx = 512
        n_threads = 4
        return GPT4All(model='./shared/language_models/model/ggml-gpt4all-l13b-snoozy.bin', n_ctx=n_ctx, n_threads=n_threads)

    def create_local_retrieval_llm(self):
        return self.create_local_llm()