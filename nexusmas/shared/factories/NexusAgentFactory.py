import os

from shared.beliefs.prompts.NexusPromptFactory import NexusPromptFactory
from langchain.agents import AgentType
from langchain.agents import initialize_agent

from shared.beliefs.prompts.NexusPromptFactory import NexusPromptFactory
from shared.brains.NexusMemory import NexusMemory
from shared.factories.language_models.NexusLLMFactory import NexusLLMFactory

class NexusAgentFactory():
    def __init__(self, *args, **kwargs):
        # do something
        pass
    
    def create_conversational_agent(self, *args, **kwargs):
        sender_str = kwargs.get("sender_str")
        verbose = os.environ.get("NEXUS_VERBOSE", "")
        if verbose.lower() == "true":
            verbose = True
        else:
            verbose = False

        if sender_str is None:
            raise Exception("sender_str is required")

        tools = kwargs.get("tools")
        if tools is None:
            raise Exception("tools is required")

        identity = kwargs.get("identity")
        personality = kwargs.get("personality")
        circumstances = kwargs.get("circumstances")
        rules = kwargs.get("rules")
        output_instructions = kwargs.get("output_instructions")
        before_prompt = kwargs.get("before_prompt")

        nexus_prompt_factory = NexusPromptFactory()
        # prompt = nexus_prompt_factory.create_chat_prompt(
        #     sender_str=sender_str,
        #     identity=identity,
        #     personality=personality,
        #     circumstances=circumstances,
        #     rules=rules,
        #     output_instructions=output_instructions,
        #     before_prompt=before_prompt
        # )

        nexus_llm_factory = NexusLLMFactory()
        memory = kwargs.get("memory", NexusMemory().get_memory([sender_str], short_term_memory_key="chat_history", disable_long_term_memory=True))

        llm = kwargs.get("llm", nexus_llm_factory.create_chat_llm())

        agent_kwargs = {
        }
        agent_chain = initialize_agent(
            tools,
            llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            # agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=verbose,
            memory=memory,
            agent_kwargs=agent_kwargs
        )

        return agent_chain
    
    # STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION has no memory
    def create_structured_tool_agent(self, *args, **kwargs):
        # TODO create a structured tool agent
        nexus_llm_factory = NexusLLMFactory()
        llm = kwargs.get("llm", nexus_llm_factory.create_chat_llm(temperature="0.9"))
        tools = kwargs.get("tools")
        intermediate_steps = kwargs.get("intermediate_steps")
        if intermediate_steps is None:
            intermediate_steps = False
        agent_chain = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True, max_iterations=20, return_intermediate_steps=intermediate_steps, handle_parsing_errors="Check your output and make sure it conforms and is escaped correctly!")
        return agent_chain
    
    def create_agent(self, *args, **kwargs):
        # do something
        # return agent
        return 1