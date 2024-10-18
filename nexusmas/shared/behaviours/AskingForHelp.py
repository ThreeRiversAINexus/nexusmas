from spade.behaviour import OneShotBehaviour
from shared.beliefs.NexusAgentDirectory import NexusAgentDirectory
from langchain.agents import load_tools
from shared.behaviours.Choosing import Choosing

class AskingForHelp(NexusAgentDirectory, OneShotBehaviour):
    def __init__(self, msg, desire, args, **kwargs):
        self.desire = desire
        self.msg = msg
        super().__init__(*args, **kwargs)

    def ask_for_help_prompt(self):
        prompt_template = "{topic}\n\n"
        return prompt_template

    async def run(self):
        print(f"{self.agent.agent_name} is asking for help")
        # given a list of agents
        # decide which agent to ask for help
        agent_directory = NexusAgentDirectory()
        agent_tools = agent_directory.get_tools(self.start_conversation, self.desire)
        tools = load_tools(agent_tools)
        Choosing(msg=self.msg, desire=self.desire, tools=tools)
        # then relay the answer to the original agent