from langchain.chains import ConversationChain
from shared.factories.language_models.NexusLLMFactory import NexusLLMFactory
from shared.brains.NexusMemory import NexusMemory
from shared.beliefs.prompts.NexusPromptFactory import NexusPromptFactory
import os

from langchain.llms import OpenAI

class NexusChainFactory():
    def __init__(self, *args, **kwargs):
        # do something
        pass

    def create_chat_chain(self, *args, **kwargs):
        sender_str = kwargs.pop("sender_str", None)
        if sender_str is None:
            raise Exception("sender_str is required")

        nexus_llm_factory = NexusLLMFactory()
        model_name = kwargs.pop("model_name", None)
        print("model_name", model_name)
        llm = kwargs.pop("llm", nexus_llm_factory.create_chat_llm(model_name=model_name))

        memory = kwargs.pop("memory", NexusMemory().get_memory([sender_str]))

        identity = kwargs.pop("identity", None)
        personality = kwargs.pop("personality", None)
        circumstances = kwargs.pop("circumstances", None)
        rules = kwargs.pop("rules", None)
        output_instructions = kwargs.pop("output_instructions", None)
        before_prompt = kwargs.pop("before_prompt", None)

        nexus_prompt_factory = NexusPromptFactory()
        prompt = kwargs.pop("prompt", nexus_prompt_factory.create_prompt(
            sender_str=sender_str,
            identity=identity,
            personality=personality,
            circumstances=circumstances,
            rules=rules,
            output_instructions=output_instructions,
            before_prompt=before_prompt
        ))

        verbose = os.environ.get("NEXUS_VERBOSE", False)
        return ConversationChain(
            llm=llm,
            memory=memory,
            prompt=prompt,
            verbose=verbose,
            input_key="input",
        )

    def create_metaprompt_chain(self, *args, **kwargs):
        return 1

    def create_dumb_chain(self, *args, **kwargs):
        # This chain should not have any prompts, and should just be a simple dumb LLM chain
        # It should still have memory, though.
        nexus_llm_factory = NexusLLMFactory()
        llm = kwargs.pop("llm", nexus_llm_factory.create_llm())
        verbose = os.environ.get("NEXUS_VERBOSE", False)
        # kwargs can include `memory=...` or mayhaps not
        conversation = ConversationChain(llm=llm, verbose=verbose, **kwargs)
        return conversation
