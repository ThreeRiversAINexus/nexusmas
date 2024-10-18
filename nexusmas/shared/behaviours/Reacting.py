from spade.behaviour import OneShotBehaviour
# Import things that are needed generically
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from shared.brains.NexusMemory import NexusMemory
from shared.factories.language_models.NexusLLMFactory import NexusLLMFactory

class Reacting(OneShotBehaviour):
    def __init__(self, msg, tools, llm=None, callback=None):
        self.msg = msg 
        self.tools = tools
        self.callback = None
        super().__init__()
        if llm is None:
            self.llm = NexusLLMFactory().create_chat_llm()
        else:
            self.llm = llm
        if callback is not None:
            self.callback = callback

    async def run(self):
        send_to = self.agent.get_sender_str(self.msg)

        # Must set the default here
        # because self.agent is None in __init__
        if self.callback is None:
            self.callback = self.agent.post_reaction

        memory = NexusMemory().get_memory([send_to], short_term_memory_key="chat_history", return_messages=True, max_token_limit=3000)

        prompt_parts = self.agent.get_prompt_parts()
        personality = prompt_parts["personality"]
        circumstances = prompt_parts["circumstances"]
        identity = prompt_parts["identity"]

        prefix = f"""
            ===
            You are {identity}
            {personality}
            {circumstances}
            ===
        """

        agent_kwargs = {
            "memory": memory,
            "system_message": prefix,
        }
        
        self.langchain_agent = initialize_agent(
            self.tools, self.llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True,
            handle_parsing_errors=True, agent_kwargs=agent_kwargs,
            max_iterations=10,
            memory=memory
        )
        self.topic = self.msg.body
        langchain_agent_output = self.langchain_agent.run(self.topic)
        if self.callback is not None:
            await self.callback(self.msg, langchain_agent_output)
        return langchain_agent_output
