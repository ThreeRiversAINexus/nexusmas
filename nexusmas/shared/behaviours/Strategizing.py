from spade.behaviour import OneShotBehaviour
from langchain.chat_models import ChatOpenAI
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner

from shared.brains.NexusMemory import NexusMemory
from shared.factories.language_models.NexusLLMFactory import NexusLLMFactory

# https://python.langchain.com/docs/use_cases/more/agents/autonomous_agents/plan_and_execute

# This is effectively an implementation of Plan-and-Execute
# My main use case for this is allowing automated
# development of the Nexus.
class Strategizing(OneShotBehaviour):
    def __init__(self, msg, tools, callback=None):
        self.msg = msg 
        self.tools = tools
        self.callback = None
        super().__init__()
        if callback is not None:
            self.callback = callback

    async def run(self):
        send_to = self.agent.get_sender_str(self.msg)

        # Must set the default here
        # because self.agent is None in __init__
        if self.callback is None:
            self.callback = self.agent.post_reaction

        # memory = NexusMemory().get_memory([send_to], short_term_memory_key="chat_history", return_messages=True, max_token_limit=3000)
        tools = self.tools
        model = ChatOpenAI(temperature=0)
        planner = load_chat_planner(model)
        executor = load_agent_executor(model, tools, verbose=True)
        executor.chain.handle_parsing_errors = "There was a problem parsing your response. Please escape special characters and make sure your output conforms."
        agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)
        # wrap agent.run in a try/catch block that repeats the question if there is an error
        # this is a hack to get around the fact that the agent will not repeat the question
        for i in range(0, 1):
            try:
                langchain_agent_output = agent.run(self.msg)
                # langchain_agent_output = "Temporarily debugging"
                # import time
                if self.callback is not None:
                    await self.callback(self.msg, langchain_agent_output)
                return langchain_agent_output
            except Exception as e:
                return "Error in Strategizing: %s" % e
                print("Repeating the question... " + str(i))
                continue
        

