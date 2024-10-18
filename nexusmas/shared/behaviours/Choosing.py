from spade.behaviour import OneShotBehaviour
from langchain.agents import initialize_agent
from langchain.agents import AgentType

from langchain.llms import OpenAI
from langchain.agents import initialize_agent

from shared.factories.language_models.NexusLLMFactory import NexusLLMFactory

class Choosing(OneShotBehaviour):
    def __init__(self, desire, tools, sender_str, choice_callback, *args, **kwargs):
        if desire is None:
            raise ValueError("Desire is None")
        super().__init__(*args, **kwargs)
        self.desire = desire
        self.sender_str = sender_str
        self.callback = choice_callback
        # memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        # if not ("past_choices" in self.agent.memories):
            
            # self.agent.memories["past_choices"] = ConversationBufferWindowMemory(input_key="topic", memory_key="chat_history", k=10) 
        # memory = self.agent.memories[O"past_choices"]
        # llmfactory = NexusLLMFactory()
        # llm = llmfactory.create_llm()
        llm = OpenAI(temperature=0.3)
        self.choosing_chain = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, handle_parsing_errors=True, max_iterations=5)

    async def run(self):
        print(f"{self.agent.identity} is choosing")
        response = self.choosing_chain.run(self.desire)
        self.set("chosen_tool_result", response)
        await self.callback(self.desire, response, self.sender_str)