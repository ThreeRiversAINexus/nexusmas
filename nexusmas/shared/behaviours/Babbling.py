from spade.behaviour import OneShotBehaviour
from spade.message import Message
from shared.factories.NexusChainFactory import NexusChainFactory
from shared.factories.NexusAgentFactory import NexusAgentFactory
from langchain.agents import Tool
from langchain.tools import ShellTool
from langchain.agents.agent_toolkits import FileManagementToolkit
# from langchain.utilities import SerpAPIWrapper
from langchain.utilities import GoogleSerperAPIWrapper
from tempfile import TemporaryDirectory
from langchain.utilities import OpenWeatherMapAPIWrapper
from langchain.agents.agent_toolkits import PlayWrightBrowserToolkit
from shared.beliefs.prompts.NexusPromptFactory import NexusPromptFactory
from langchain.tools.playwright.utils import (
    create_async_playwright_browser,
    create_sync_playwright_browser,  # A synchronous browser is available, though it isn't compatible with jupyter.
)

from shared.behaviours.Picking import Picking
import os

class Babbling(OneShotBehaviour):
    def __init__(self, *args, **kwargs):
        self.topic = kwargs.pop("topic", None)
        self.babbling_to = kwargs.pop("babbling_to", None)
        self.model_name = kwargs.pop("model_name", "gpt-3.5-turbo")

        super().__init__(*args, **kwargs)

    def get_tools(self):
        tools = []
        # async_browser = create_async_playwright_browser()
        # toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
        # tools += toolkit.get_tools()
        search = GoogleSerperAPIWrapper()
        # pipshell_tool = ShellTool()
        working_directory = "/"

        tools += FileManagementToolkit(
            root_dir=str(working_directory),
            selected_tools=["read_file", "list_directory"],
        ).get_tools()
        tools += [
            Tool(
                name = "Current Search",
                func=search.run,
                description="useful for when you need to answer questions about current events or the current state of the world. the input to this should be a single search term."
            ),
        ]
        # tools += [
        #     shell_tool
        # ]
        return tools

    def escape_braces(self, text):
        return text.replace("{", "{{").replace("}", "}}")

    async def run(self):
        msg = Message(to=self.babbling_to)
        msg.set_metadata("performative", "inform")
        msg.set_metadata("ontology", "the-nexus-multi-agent-system")
        # choices = [
        #     "Make a joke",
        #     "Ask a question",
        #     "Tell a story",
        #     "Make a statement",
        # ]
        # picker = Picking("You are in a chat with your creator.", choices)
        # picked = await picker.run()
        # from pprint import pprint
        # pprint(picked)
        prompt_parts = self.agent.get_prompt_parts()
        self.chain = NexusChainFactory().create_chat_chain(
            sender_str=self.babbling_to,
            model_name=self.model_name,
            **prompt_parts,
        )
        
        input_tokens = self.chain.llm.get_num_tokens(self.topic)
        msg.body = self.chain.predict(input=self.topic)
        output_tokens = self.chain.llm.get_num_tokens(msg.body)
        print(f"{self.agent.identity} is babbling to {self.babbling_to} about: {msg.body}\nTokens in Input: {input_tokens}\nTokens in Output: {output_tokens}")
        await self.send(msg)